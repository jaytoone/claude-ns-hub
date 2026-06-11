#!/usr/bin/env python3
"""
Stop hook: inject pending-execute-queue.jsonl entries when Claude stops inside
a provider-exec-{proj} tmux session. Also captures session_id for all sessions.

Guards: tmux session name matches "*-exec-*" → cwd maps to project →
queue has unconsumed bytes OR queued milestones remain.

Dispatch: JSON stdout (decision:block + additionalContext) — preferred over
exit-2/stderr. Falls back to stderr+exit(2) if JSON encode fails.
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _ns_utils import get_exec_tmux_session, exec_session_main, PROJECTS_DIR


def _hub_api() -> str:
    """Discover hub API URL. NS_HUB_URL env var takes priority (dev/prod branching)."""
    import os as _os
    if url := _os.environ.get("NS_HUB_URL"):
        return url.rstrip("/")
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=2)
        for line in r.stdout.splitlines():
            if ":9001" in line and "LISTEN" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+):9001", line)
                if m:
                    return f"http://{m.group(1)}:9001"
    except Exception:
        pass
    return "http://127.0.0.1:9001"


def _get_queued_milestones(proj_id: str) -> list:
    """Fetch remaining queued+actionable milestones. Tries SQLite direct first (fast),
    falls back to HTTP API. M445: direct DB avoids network round-trip (~1ms vs ~50ms)."""
    # --- SQLite direct path ---
    try:
        import sqlite3
        db_path = PROJECTS_DIR.parent / "ns-events.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path), timeout=2)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT data_json FROM milestones_store WHERE proj_id=? AND status='queued' AND (held IS NULL OR held=0) AND (done IS NULL OR done=0)",
                (proj_id,)
            ).fetchall()
            conn.close()
            results = []
            for row in rows:
                try:
                    m = json.loads(row["data_json"])
                    if str(m.get("text", "")).strip():
                        results.append(m)
                except Exception:
                    pass
            if results:
                return results
    except Exception:
        pass
    # --- HTTP API fallback ---
    try:
        hub = _hub_api()
        req = urllib.request.Request(f"{hub}/api/northstar/{proj_id}/milestones")
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
        return [
            m for m in data.get("milestones", [])
            if m.get("status") == "queued"
            and not m.get("held")
            and not m.get("done")
            and str(m.get("text", "")).strip()
        ]
    except Exception:
        return []


def _continuation_allowed(pdir: Path, sid: str) -> bool:
    """Rate-limit re-injection: max 5 consecutive attempts without REAL progress,
    and max 10 total injections per session (prevents infinite loops when stones stay queued).
    M845 fix: "real progress" = a NEW unique milestone_id appears in completion-log (i.e. a
    different stone advanced). Previously any log_size growth (including benign comments on
    the SAME stone) was treated as progress → infinite loop on a single stuck stone."""
    attempt_file = pdir / ".stop-requeue-attempt"
    log_file = pdir / "completion-log.jsonl"

    # Read current attempt state
    state = {}
    if attempt_file.exists():
        try:
            state = json.loads(attempt_file.read_text())
        except Exception:
            state = {}

    # If session changed, reset counter
    if state.get("sid") != sid:
        state = {"sid": sid, "count": 0, "total": 0, "seen_mids": []}

    # Hard cap: max 10 total injections per session regardless of progress
    if state.get("total", 0) >= 10:
        return False

    # M845 fix: scan completion-log for unique milestone_ids; reset count only when a NEW mid appears.
    # Repeated entries for the same mid (benign comment loops) do NOT count as progress.
    _new_mids: set = set()
    _prev_seen = set(state.get("seen_mids", []))
    if log_file.exists():
        try:
            for line in log_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.strip():
                    continue
                try:
                    _e = json.loads(line)
                    _mid = _e.get("milestone_id")
                    if _mid:
                        _new_mids.add(_mid)
                except Exception:
                    pass
        except Exception:
            pass
    _delta_mids = _new_mids - _prev_seen
    if _delta_mids:
        state["count"] = 0  # genuinely-new stone advanced → reset consecutive attempt counter
        state["seen_mids"] = sorted(_new_mids)[-200:]  # cap memory; keep recent 200 mids

    if state["count"] >= 5:
        return False  # 5 consecutive attempts without new-mid progress → stop re-injecting

    state["count"] += 1
    state["total"] = state.get("total", 0) + 1
    if not state.get("seen_mids"):
        state["seen_mids"] = sorted(_new_mids)[-200:]
    try:
        attempt_file.write_text(json.dumps(state))
    except Exception:
        pass
    return True


def _emit_block(reason_short: str, body: str, count: int, idle_file: "Path | None" = None):
    """Block stop via JSON decision:block + additionalContext (M504).
    Preferred over exit-2/stderr: clean channel separation, suppressOutput support,
    10k-char limit enforced. Falls back to stderr+exit(2) on encode failure."""
    # M536: delete idle file — we're re-injecting work, not truly idle
    if idle_file is not None:
        try:
            idle_file.unlink(missing_ok=True)
        except Exception:
            pass
    header = (
        f"## AUTONOMOUS TASK DISPATCH ({count} queued entr"
        f"{'y' if count == 1 else 'ies'} via Execute button)\n"
        "Process these instructions now.\n\n"
    )
    ctx = header + body
    if len(ctx) > 9500:
        ctx = ctx[:9500] + "\n\n[...truncated — see queue file for full content]"
    try:
        print(json.dumps({
            "decision": "block",
            "reason": reason_short,
            "suppressOutput": True,
            "systemMessage": ctx,
        }, ensure_ascii=False))
        sys.exit(0)
    except Exception:
        sys.stderr.write(header + body + "\n")
        sys.exit(2)


def get_project_id(cwd: str):
    """Map cwd to project_id by scanning PROJECTS_DIR at runtime — no hardcoded list."""
    if not PROJECTS_DIR.exists():
        return None
    cwd_parts = {p.lower() for p in Path(cwd).parts}
    for proj_dir in PROJECTS_DIR.iterdir():
        if proj_dir.is_dir() and proj_dir.name.lower() in cwd_parts:
            return proj_dir.name
    return None


def _read_frontmatter_fields(md_path: Path, *keys) -> dict:
    """Extract scalar fields from YAML frontmatter."""
    result = {k: "" for k in keys}
    try:
        txt = md_path.read_text(encoding="utf-8")
        if txt.startswith("---"):
            end = txt.find("\n---", 3)
            block = txt[3:end] if end > 0 else ""
            for k in keys:
                m = re.search(rf"^{k}:\s*['\"]?([^'\"\\n]+)['\"]?", block, re.MULTILINE)
                if m:
                    result[k] = m.group(1).strip()
    except Exception:
        pass
    return result


def _extract_stone_facts(stone: dict) -> dict:
    """M520: accuracy-first fact extraction — store exact quoted text, not LLM summaries."""
    facts: dict = {"decisions": [], "errors": [], "constraints": [], "state": []}
    text = (stone.get("text") or "").strip()
    if text:
        facts["state"].append(f"Task: {text[:200]}")
    conv = stone.get("conversation") or []
    for entry in conv:
        content = str(entry.get("content") or "").strip()
        if not content:
            continue
        for line in content.split("\n"):
            ls = line.lower().strip()
            if any(p in ls for p in ("decided:", "decision:", "결정:", "chose:", "선택:", "confirmed:", "approach:")):
                facts["decisions"].append(line.strip()[:200])
            elif any(p in ls for p in ("error:", "bug:", "fix:", "오류:", "fixed:", "issue:", "root cause:")):
                facts["errors"].append(line.strip()[:200])
            elif any(p in ls for p in ("constraint:", "rule:", "never:", "always:", "must not:", "제약:", "금지:")):
                facts["constraints"].append(line.strip()[:200])
    if stone.get("star_relation"):
        facts["state"].append(f"Result: {stone['star_relation']}")
    # Deduplicate
    for k in facts:
        seen: set = set()
        deduped = []
        for v in facts[k]:
            if v not in seen:
                seen.add(v)
                deduped.append(v)
        facts[k] = deduped[:5]  # cap at 5 per category
    return facts


def _save_stone_memory(pdir: Path, stone: dict):
    """Save extracted facts to .stone-memory/{stone_id}.jsonl (M520)."""
    stone_id = stone.get("id")
    if not stone_id:
        return
    mem_dir = pdir / ".stone-memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    mem_file = mem_dir / f"{stone_id}.jsonl"
    # Only re-extract if file missing or stone was updated since last extract
    confirm_at = stone.get("pending_confirm_at") or stone.get("exec_end") or ""
    if mem_file.exists():
        try:
            existing = json.loads(mem_file.read_text().splitlines()[0])
            if existing.get("confirm_at") == confirm_at:
                return  # already up-to-date
        except Exception:
            pass
    facts = _extract_stone_facts(stone)
    entry = {
        "stone_id": stone_id,
        "ts": datetime.datetime.now().isoformat(),
        "confirm_at": confirm_at,
        "facts": facts,
    }
    try:
        mem_file.write_text(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _extract_recent_completions(proj_id: str, pdir: Path):
    """M520: scan recently completed stones and save their facts to .stone-memory/."""
    cutoff = (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat()
    try:
        import sqlite3
        db_path = PROJECTS_DIR.parent / "ns-events.db"
        if not db_path.exists():
            return
        conn = sqlite3.connect(str(db_path), timeout=2)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT data_json FROM milestones_store WHERE proj_id=?",
            (proj_id,)
        ).fetchall()
        conn.close()
        for row in rows:
            try:
                stone = json.loads(row["data_json"])
                confirm_at = stone.get("pending_confirm_at") or ""
                status = stone.get("status", "")
                if status in ("pending_confirmation", "done") and confirm_at >= cutoff:
                    _save_stone_memory(pdir, stone)
            except Exception:
                pass
    except Exception:
        pass


def _load_stone_memory(pdir: Path, limit: int = 6) -> str:
    """M520: load recent stone memories, return formatted section for Execute prompt."""
    mem_dir = pdir / ".stone-memory"
    if not mem_dir.exists():
        return ""
    entries = []
    cutoff = (datetime.datetime.now() - datetime.timedelta(hours=48)).isoformat()
    for p in sorted(mem_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]:
        try:
            raw = p.read_text().splitlines()[0]
            e = json.loads(raw)
            if e.get("ts", "") < cutoff:
                continue
            f = e.get("facts", {})
            lines = []
            for cat, items in f.items():
                for item in items:
                    lines.append(f"  [{cat}] {item}")
            if lines:
                entries.append(f"  [{e['stone_id']}]\n" + "\n".join(lines))
        except Exception:
            continue
    if not entries:
        return ""
    return "STONE MEMORY (facts from recently completed stones — use for context):\n" + "\n".join(entries) + "\n\n"



_HUB_COMPLETE_RE = re.compile(r'^\s*\{"__hub__"\s*:\s*"complete"', re.MULTILINE)


def _apply_hub_complete_blocks(proj_id: str, transcript_path: str, hub: str):
    """Passive LLM mode: parse {"__hub__":"complete",...} sentinels from last assistant
    turn in transcript and PATCH hub directly — LLM needs no direct API call."""
    try:
        tp = Path(transcript_path)
        if not tp.exists():
            return
        lines = tp.read_text(encoding="utf-8", errors="ignore").splitlines()
        last_text = ""
        for line in reversed(lines[-300:]):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant":
                    for block in (entry.get("message") or {}).get("content") or []:
                        if isinstance(block, dict) and block.get("type") == "text":
                            last_text = block.get("text", "")
                            break
                    if last_text:
                        break
            except Exception:
                continue
        if not last_text:
            return
        for raw_line in last_text.splitlines():
            s = raw_line.strip()
            if not s.startswith('{"__hub__"'):
                continue
            try:
                payload = json.loads(s)
                if payload.get("__hub__") != "complete":
                    continue
                mid = payload.get("mid", "").strip()
                if not mid:
                    continue
                patch = {
                    "status": payload.get("status", "pending_confirmation"),
                    "model_used": "auto",
                    "pending_confirm_at": datetime.datetime.now().isoformat(),
                }
                if reply := payload.get("reply", ""):
                    patch["append_message"] = {"role": "claude", "text": reply}
                if star := payload.get("star", ""):
                    patch["star_relation"] = star
                req = urllib.request.Request(
                    f"{hub}/api/northstar/{proj_id}/milestones/{mid}/",
                    data=json.dumps(patch).encode(),
                    headers={"Content-Type": "application/json"},
                    method="PATCH",
                )
                urllib.request.urlopen(req, timeout=3).read()
            except Exception:
                continue
    except Exception:
        pass


_STONE_ID_RE = re.compile(r'\b(M\d{3,5})\b')
_COMPLETION_KW = re.compile(
    r'(완료|done|completed|finished|구현|적용|수정|패치|pending_confirmation'
    r'|PATCH.*status|status.*pending|✅|⇒\s*done)',
    re.IGNORECASE,
)


def _detect_completion_by_transcript(proj_id: str, transcript_path: str, hub: str):
    """Fallback completion detection: no sentinel required.
    Finds queued stone IDs mentioned near completion language in last assistant turn."""
    try:
        queued = _get_queued_milestones(proj_id)
        if not queued:
            return
        queued_ids = {str(m.get("id", "")).strip() for m in queued if m.get("id")}
        if not queued_ids:
            return

        tp = Path(transcript_path)
        if not tp.exists():
            return
        raw_lines = tp.read_text(encoding="utf-8", errors="ignore").splitlines()
        last_text = ""
        for line in reversed(raw_lines[-300:]):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant":
                    for block in (entry.get("message") or {}).get("content") or []:
                        if isinstance(block, dict) and block.get("type") == "text":
                            last_text = block.get("text", "")
                            break
                    if last_text:
                        break
            except Exception:
                continue
        if not last_text or len(last_text) < 20:
            return

        # Only look at last 800 chars — completion statements are at the end
        tail = last_text[-800:]
        if not _COMPLETION_KW.search(tail):
            return

        mentioned = set(_STONE_ID_RE.findall(tail))
        matches = queued_ids & mentioned
        if not matches:
            return

        for mid in matches:
            try:
                # Extract reply: first line in tail that mentions the stone ID
                reply_line = next(
                    (ln.strip() for ln in tail.splitlines() if mid in ln and ln.strip()),
                    f"{mid} 완료"
                )[:120]
                patch = {
                    "status": "pending_confirmation",
                    "model_used": "auto-transcript",
                    "pending_confirm_at": datetime.datetime.now().isoformat(),
                    "append_message": {"role": "claude", "text": reply_line},
                    "star_relation": "transcript-detected completion (no sentinel)",
                }
                req = urllib.request.Request(
                    f"{hub}/api/northstar/{proj_id}/milestones/{mid}/",
                    data=json.dumps(patch).encode(),
                    headers={"Content-Type": "application/json"},
                    method="PATCH",
                )
                urllib.request.urlopen(req, timeout=3).read()
            except Exception:
                continue
    except Exception:
        pass


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    cwd = data.get("cwd", "")
    proj_id = get_project_id(cwd)
    if not proj_id:
        return

    pdir = PROJECTS_DIR / proj_id
    is_exec = get_exec_tmux_session() is not None

    # Capture session_id for all session types (exec + interactive)
    sid = data.get("session_id")
    if sid:
        try:
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / ".last-session-id").write_text(sid)
            fm = _read_frontmatter_fields(pdir / "north-star.md", "model", "continuity_mode")
            cur_model, continuity_mode = fm["model"], fm["continuity_mode"] or "isolated"
            hist_file = pdir / ".session-history.json"
            hist = {}
            if hist_file.exists():
                try: hist = json.loads(hist_file.read_text())
                except Exception: pass
            if is_exec:
                hist[cur_model or "_default"] = sid
                if continuity_mode == "portable":
                    hist["_current"] = sid
            else:
                hist["_interactive"] = sid
            hist_file.write_text(json.dumps(hist, indent=2))
        except Exception:
            pass

    if not is_exec:
        return

    # M536: write .exec-idle sentinel — Claude stopped in exec session.
    _idle_file = pdir / ".exec-idle"
    try:
        _idle_file.write_text(datetime.datetime.now().isoformat())
    except Exception:
        pass

    # M1206: immediate auto-reply trigger — wake worker right now instead of waiting 60s poll.
    try:
        _trigger_req = urllib.request.Request(
            f"{_hub_api()}/api/northstar/{proj_id}/trigger-auto-reply",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(_trigger_req, timeout=3)
    except Exception:
        pass  # non-critical: worker will pick up on next 60s poll

    # M520: extract facts from recently completed stones (metadata only, no injection)
    try:
        _extract_recent_completions(proj_id, pdir)
    except Exception:
        pass

    # MCP check: if session has MCP config, Claude already called report_task_complete()
    # during execution — skip all completion detection and re-injection entirely.
    _tmux_sess = get_exec_tmux_session()
    if _tmux_sess and Path(f"/tmp/hub/mcp/{_tmux_sess}.json").exists():
        return  # MCP session: no sentinel parsing, no re-injection needed

    # Legacy path: parse hub-complete sentinels + transcript fallback
    tp = data.get("transcript_path", "")
    hub = _hub_api()
    if tp:
        try:
            _apply_hub_complete_blocks(proj_id, tp, hub)
        except Exception:
            pass
        try:
            _detect_completion_by_transcript(proj_id, tp, hub)
        except Exception:
            pass

    queue = pdir / "pending-execute-queue.jsonl"
    if not queue.exists():
        return

    offset_file = pdir / ".queue-offset"
    try:
        offset = int(offset_file.read_text().strip()) if offset_file.exists() else 0
    except Exception:
        offset = 0

    try:
        file_size = queue.stat().st_size
    except Exception:
        return

    if file_size <= offset:
        # No new queue entries — check if queued milestones remain (M386/M443 fix)
        queued = _get_queued_milestones(proj_id)
        # M837 Stage 1.5: filter queued to stones owned by THIS tmux session.
        # Prior bug: main stop-hook injected ALL queued stones including those
        # assigned to branched sessions → main grabbed branched-owned work.
        # Owner rule:
        #   - current session == main (provider-exec-{proj}) → include unassigned + main-assigned
        #   - current session == branched (provider-exec-{proj}-{suffix}) → include only that suffix's assigned
        try:
            _cur_sess = get_exec_tmux_session() or exec_session_main()
            # Build substar_id → assigned_session map from north_stars
            _ns_resp = subprocess.run(
                ["curl", "-s", f"{_hub_api()}/api/northstar/{proj_id}/north-stars"],
                capture_output=True, text=True, timeout=3,
            )
            _ns_data = json.loads(_ns_resp.stdout) if _ns_resp.returncode == 0 else {}
            _ns_list = _ns_data.get("north_stars") or []
            _assign_by_sid = {ns.get("id"): (ns.get("assigned_session") or "").strip() for ns in _ns_list if ns.get("id")}
            def _stone_owner(m):
                _sid = m.get("substar_id") or ""
                if not _sid:
                    return exec_session_main(_cur_sess)  # ungrouped → main
                return _assign_by_sid.get(_sid) or exec_session_main(_cur_sess)
            _before = len(queued)
            queued = [m for m in queued if _stone_owner(m) == _cur_sess]
            if _before != len(queued):
                # Drop counts logged via append below; emit early-debug to stderr suppressed
                pass
        except Exception:
            # On filter failure, keep original list (safe fallback — no regression)
            pass
        if queued and _continuation_allowed(pdir, sid or ""):
            hub = _hub_api()
            # M443: write a proper queue entry (same format as Execute button) so the
            # queue+offset path handles dispatch — eliminates fragile free-text stderr injection.
            def _ms_line(m):
                line = f"  {m.get('id')} [{m.get('status')}]: \"{m.get('text','')[:60]}\""
                for ref in (m.get("skill_refs") or ([m["skill_ref"]] if m.get("skill_ref") else [])):
                    line += f"  [skill: /{ref}]"
                for ref in (m.get("agent_refs") or ([m["agent_ref"]] if m.get("agent_ref") else [])):
                    line += f"  [agent: {ref}]"
                return line
            # M752: split queued stones into impl vs Q&A (last conv entry = user → reply only)
            def _is_qa_stone(m):
                conv = m.get("conversation") or []
                return bool(conv) and conv[-1].get("role") == "user"
            qa_stones   = [m for m in queued if _is_qa_stone(m)]
            impl_stones = [m for m in queued if not _is_qa_stone(m)]

            # M472: classify impl_stones into parallel (independent) vs serial (parent_id dependency)
            queued_ids = {m["id"] for m in impl_stones}
            parallel = [m for m in impl_stones if not (m.get("parent_id") and m["parent_id"] in queued_ids)]
            serial   = [m for m in impl_stones if m.get("parent_id") and m["parent_id"] in queued_ids]
            impl_lines = "\n".join(_ms_line(m) for m in impl_stones)
            # M570: compact dispatch body — 68% token reduction vs verbose format
            mem_section = _load_stone_memory(pdir)
            if len(parallel) >= 2:
                par_ids = " ".join(m["id"] for m in parallel)
                ser_clause = ""
                if serial:
                    ser_clause = f" | SERIAL after: {' '.join(m['id'] for m in serial)}"
                dispatch_line = f"DISPATCH PARALLEL: emit {par_ids} as simultaneous Agent calls in ONE message{ser_clause}.\n"
            elif impl_stones:
                dispatch_line = f"DISPATCH SERIAL: implement each stone sequentially.\n"
            else:
                dispatch_line = ""
            # Build Q&A section if any Q&A stones (M752: separate from impl to prevent re-implementation)
            qa_section = ""
            if qa_stones:
                qa_ids = " ".join(m["id"] for m in qa_stones)
                qa_previews = "\n".join(
                    f"  {m['id']}: user asked → \"{(m.get('conversation') or [{}])[-1].get('text','')[:80]}\""
                    for m in qa_stones
                )
                qa_section = (
                    f"\nQ&A REPLY (these stones have a user question — reply only, do NOT re-implement):\n"
                    f"  {qa_ids}\n"
                    f"{qa_previews}\n"
                    f"  For each: PATCH append_message{{role:'claude', text:'<≤3 line answer>'}} ONLY.\n"
                    f"  Do NOT set status=pending_confirmation on these Q&A stones.\n"
                )
            # Build impl section
            impl_section = ""
            if impl_stones:
                impl_section = (
                    f"COMPLETION SENTINEL (output after each stone, on its own line, no markdown/code-fence):\n"
                    f'  {{"__hub__":"complete","mid":"<STONE_ID>","status":"pending_confirmation","reply":"<1-line past-tense>","star":"child|parent|none"}}\n'
                    f"COMMENT: ≤3 lines. Detail → docs/ns-replies/<DATE>-<MID>.md + ref link.\n"
                    f"UI PROOF: Playwright screenshot → rclone gdrive:claude-shared/Moat/outbox/ → link in comment.\n"
                    f"NO-OP: if skipping, output sentinel with status:skipped and reply explaining why.\n"
                    f"\nImpl stones:\n{impl_lines}"
                )
            body = (
                f"[EXECUTE SYNC] {len(queued)} queued stone(s) ({len(impl_stones)} impl / {len(qa_stones)} Q&A).\n"
                f"{mem_section}"
                f"GET {hub}/api/northstar/{proj_id}/milestones → read full text+conversation[].\n"
                f"{dispatch_line}"
                f"{impl_section}"
                f"{qa_section}"
            )
            # Write proper queue entry — same structure as Execute button generates.
            # Offset stays at old file_size so this new entry is picked up on next stop.
            entry = json.dumps({"ts": datetime.datetime.now().isoformat(), "body": body}, ensure_ascii=False)
            try:
                with queue.open("a", encoding="utf-8") as _qh:
                    _qh.write(entry + "\n")
                # Leave offset at old file_size — new entry will be consumed on next stop.
                # (offset_file already points to old file_size; do not advance it here)
            except Exception:
                pass
            _emit_block(f"{len(queued)} queued stone(s) — continuing", body, len(queued), _idle_file)
        return

    try:
        with queue.open("r", encoding="utf-8") as f:
            f.seek(offset)
            new_data = f.read()
    except Exception:
        return

    entries = [json.loads(l) for l in new_data.splitlines() if l.strip() and _safe_json(l)]

    try:
        offset_file.write_text(str(file_size))
    except Exception:
        pass

    if not entries:
        return

    # M422: deduplicate — multiple EXECUTE SYNC entries collapse to the last one.
    # REPLY SYNC entries are unique per stone and always kept.
    # Prevents Claude seeing the same dispatch prompt N times when Execute clicked N times.
    reply_entries = [e for e in entries if "[REPLY SYNC]" in e.get("body", "") and "[EXECUTE SYNC]" not in e.get("body", "")]
    exec_entries  = [e for e in entries if "[EXECUTE SYNC]" in e.get("body", "") and "[REPLY SYNC]" not in e.get("body", "")]
    mixed_entries = [e for e in entries if "[REPLY SYNC]" in e.get("body", "") and "[EXECUTE SYNC]" in e.get("body", "")]
    out_bodies = [e.get("body", "") for e in reply_entries + mixed_entries]
    if exec_entries:
        out_bodies.append(exec_entries[-1].get("body", ""))  # only last EXECUTE SYNC
    bodies = "\n\n---\n\n".join(b for b in out_bodies if b)
    total = len(reply_entries) + len(mixed_entries) + (1 if exec_entries else 0)
    _emit_block(f"{total} queued entr{'y' if total==1 else 'ies'} via Execute button", bodies, total, _idle_file)


def _safe_json(line: str):
    try: return json.loads(line)
    except Exception: return None


if __name__ == "__main__":
    main()
