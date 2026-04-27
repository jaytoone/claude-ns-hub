#!/usr/bin/env python3
"""ctx-validate — CTX utility reproducibility receipt.

Runs a tool-aware utility measurement on ANY set of Claude Code transcripts
and emits a 1-page markdown report with Wilson 95% CIs. Designed as a
distribution asset: a skeptical user can run this on their own transcripts
and get a reproducible number before deciding whether to install/pay for CTX.

Usage:
  python3 ctx_validate.py                                    # auto-detect ~/.claude/projects/
  python3 ctx_validate.py --days 14                          # wider window
  python3 ctx_validate.py --project-dir <path>               # specific project
  python3 ctx_validate.py --transcript-dir <jsonl-dir>       # specific directory
  python3 ctx_validate.py --out report.md                    # write to file

Output: markdown to stdout (or --out file). Returns exit code 0 on success,
non-zero on hard errors (missing transcripts, etc.).

Dependencies: stdlib only. No network calls. No telemetry. No uploads.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

HOME = Path(os.path.expanduser("~"))
DEFAULT_PROJECTS_DIR = HOME / ".claude" / "projects"

# Keys from tool_use block inputs that carry meaningful referenceable content.
# Matches the live utility-rate.py hook so the offline script and the live
# metric see the same signal surface.
_TOOL_USE_STRING_KEYS = {
    "file_path", "notebook_path", "command", "pattern", "path",
    "description", "prompt", "query", "url", "old_string", "new_string",
    "subagent_type",
}


# ───────────────────────────── statistics ──────────────────────────────

def wilson_ci(y: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95% confidence interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = y / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fmt_rate(y: int, n: int) -> str:
    if n == 0:
        return "— (n=0)"
    p = y / n
    lo, hi = wilson_ci(y, n)
    half = (hi - lo) * 50
    return f"**{p:.1%}** 95% CI [{lo:.1%}, {hi:.1%}] ±{half:.1f}pp (n={n})"


# ───────────────────────────── transcript parsing ──────────────────────

def _project_dir_to_cwd(project_name: str) -> Optional[str]:
    """Reverse Claude Code's '/' → '-' project-dir encoding."""
    if not project_name.startswith("-"):
        return None
    cwd = project_name.replace("-", "/")
    return cwd if os.path.isdir(cwd) else None


def _extract_tool_params(content: list) -> str:
    parts: list[str] = []
    for c in content or []:
        if not (isinstance(c, dict) and c.get("type") == "tool_use"):
            continue
        name = c.get("name", "")
        if name:
            parts.append(name)
        inp = c.get("input", {}) or {}
        for k, v in inp.items():
            if k not in _TOOL_USE_STRING_KEYS:
                continue
            if isinstance(v, str):
                parts.append(v[:800])
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        parts.append(item[:400])
    return "\n".join(parts)[:4000]


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            t = c.get("text", "")
            if t and t.strip():
                parts.append(t)
    return "\n".join(parts)


def _classify_response_type(resp_len: int, tool_len: int) -> str:
    if resp_len + tool_len == 0:
        return "unknown"
    tool_share = tool_len / (resp_len + tool_len)
    if tool_share >= 0.5 and resp_len < 400:
        return "tool_heavy"
    if tool_share >= 0.2:
        return "mixed"
    return "prose"


def _iter_user_assistant_pairs(transcript_path: Path) -> Iterable[tuple]:
    """Yield (user_prompt, response_text, tool_params) for each user→assistant
    adjacency. One pair per user message, aggregating all assistant blocks
    that follow until the next user message."""
    last_user: Optional[str] = None
    resp_text: list[str] = []
    resp_tool: list[str] = []
    emitted = True
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except Exception:
                    continue
                t = d.get("type")
                if t == "user":
                    if last_user and not emitted and (resp_text or resp_tool):
                        yield (last_user, "\n".join(resp_text),
                               "\n".join(resp_tool)[:4000])
                        emitted = True
                    content = d.get("message", {}).get("content", "")
                    last_user = _extract_text(content)
                    resp_text = []
                    resp_tool = []
                    emitted = False
                    continue
                if t != "assistant":
                    continue
                content = d.get("message", {}).get("content", [])
                text = _extract_text(content)
                if text:
                    resp_text.append(text)
                tp = _extract_tool_params(content)
                if tp:
                    resp_tool.append(tp)
    except Exception:
        return
    if last_user and not emitted and (resp_text or resp_tool):
        yield (last_user, "\n".join(resp_text), "\n".join(resp_tool)[:4000])


# ───────────────────────────── scoring ─────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Minimal tokenizer — avoids any CTX-specific tokenizer dependency so the
    script is self-contained. Matches the practical behavior of the live
    hook's substring check: word-boundaries + compound/hyphen preservation."""
    import re
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{3,}", text)
    return [t.lower() for t in tokens]


def _score_pair(prompt_text: str, response_text: str, tool_params: str,
                key_terms: list[str]) -> dict:
    """Check how many of the query's distinctive terms surface in the
    assistant's actions (response_text + tool_params). Simulates CTX's
    substring+tool hit signal without needing the actual hook's injection
    trace — this is what validates "CTX would have been useful here" in a
    reproducibility test.
    """
    rl = response_text.lower()
    tl = tool_params.lower()
    hits_text = sum(1 for t in key_terms if len(t) >= 4 and t in rl)
    hits_tool = sum(1 for t in key_terms if len(t) >= 4 and t in tl)
    hits_either = sum(1 for t in key_terms
                      if len(t) >= 4 and (t in rl or t in tl))
    return {
        "n_terms": len(key_terms),
        "hits_text": hits_text,
        "hits_tool": hits_tool,
        "hits_either": hits_either,
        "tool_only": max(0, hits_either - hits_text),
    }


def _distinctive_terms(prompt: str, max_terms: int = 8) -> list[str]:
    """Extract the query's most distinctive terms. Filters common English
    words + CTX-irrelevant generic tokens. Used as the scoring key-set per
    pair — if CTX were wired, these are the tokens it would most likely
    bring into context from prior sessions."""
    tokens = _tokenize(prompt)
    stop = {
        "this", "that", "what", "when", "where", "which", "would", "should",
        "could", "have", "been", "your", "with", "from", "they", "their",
        "them", "also", "only", "than", "then", "more", "most", "some",
        "most", "does", "like", "just", "want", "need", "make", "will",
        "going", "know", "take", "show", "something", "anything",
    }
    seen = set()
    out = []
    for t in tokens:
        if t in stop or t in seen:
            continue
        seen.add(t)
        out.append(t)
        if len(out) >= max_terms:
            break
    return out


# ───────────────────────────── main validate ───────────────────────────

def find_transcripts(project_dir: Optional[str], transcript_dir: Optional[str],
                     days: int) -> list[Path]:
    cutoff = time.time() - days * 86400
    files: list[Path] = []
    if transcript_dir:
        tdir = Path(transcript_dir)
        if not tdir.is_dir():
            return []
        files = [f for f in tdir.glob("*.jsonl") if f.stat().st_mtime >= cutoff]
    elif project_dir:
        pname = project_dir.rstrip("/").replace("/", "-")
        tdir = DEFAULT_PROJECTS_DIR / pname
        if not tdir.is_dir():
            return []
        files = [f for f in tdir.glob("*.jsonl") if f.stat().st_mtime >= cutoff]
    else:
        if not DEFAULT_PROJECTS_DIR.is_dir():
            return []
        for proj in DEFAULT_PROJECTS_DIR.iterdir():
            if not proj.is_dir():
                continue
            for f in proj.glob("*.jsonl"):
                if f.stat().st_mtime >= cutoff:
                    files.append(f)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def validate(project_dir: Optional[str], transcript_dir: Optional[str],
             days: int, min_prompt_len: int, min_response_len: int,
             max_pairs: int) -> dict:
    transcripts = find_transcripts(project_dir, transcript_dir, days)
    if not transcripts:
        return {"error": "no transcripts found",
                "checked_days": days,
                "project_dir": project_dir,
                "transcript_dir": transcript_dir}

    pairs = []
    for tpath in transcripts:
        proj = tpath.parent.name
        for (p, r_text, r_tool) in _iter_user_assistant_pairs(tpath):
            if len(p) < min_prompt_len:
                continue
            if p.startswith(("<command-", "Caveat:", "[tool_")):
                continue
            if len(r_text) < min_response_len and len(r_tool) < 40:
                continue
            pairs.append({"prompt": p, "response": r_text,
                          "tool_params": r_tool, "project": proj})
            if len(pairs) >= max_pairs:
                break
        if len(pairs) >= max_pairs:
            break

    if not pairs:
        return {"error": "no usable (user, assistant) pairs matched filters",
                "transcripts_found": len(transcripts)}

    total_terms = 0
    total_text_hits = 0
    total_tool_hits = 0
    total_either_hits = 0
    total_tool_only = 0
    by_rtype: dict = defaultdict(lambda: {"pairs": 0, "terms": 0, "either": 0})
    for pair in pairs:
        terms = _distinctive_terms(pair["prompt"])
        if not terms:
            continue
        s = _score_pair(pair["prompt"], pair["response"],
                        pair["tool_params"], terms)
        total_terms += s["n_terms"]
        total_text_hits += s["hits_text"]
        total_tool_hits += s["hits_tool"]
        total_either_hits += s["hits_either"]
        total_tool_only += s["tool_only"]
        rtype = _classify_response_type(len(pair["response"]),
                                        len(pair["tool_params"]))
        by_rtype[rtype]["pairs"] += 1
        by_rtype[rtype]["terms"] += s["n_terms"]
        by_rtype[rtype]["either"] += s["hits_either"]

    return {
        "n_pairs": len(pairs),
        "n_projects": len(set(p["project"] for p in pairs)),
        "n_transcripts": len(transcripts),
        "total_terms": total_terms,
        "text_hits": total_text_hits,
        "tool_hits": total_tool_hits,
        "either_hits": total_either_hits,
        "tool_only_hits": total_tool_only,
        "text_rate": total_text_hits / total_terms if total_terms else 0,
        "tool_rate": total_tool_hits / total_terms if total_terms else 0,
        "either_rate": total_either_hits / total_terms if total_terms else 0,
        "by_rtype": dict(by_rtype),
        "window_days": days,
    }


def render_markdown(result: dict) -> str:
    if result.get("error"):
        return (f"# CTX Validation — failed\n\n"
                f"Error: {result['error']}\n\n"
                f"Checked: project_dir={result.get('project_dir')} "
                f"transcript_dir={result.get('transcript_dir')} "
                f"days={result.get('checked_days', result.get('window_days'))}\n")

    r = result
    lines = []
    lines.append(f"# CTX Validation Receipt ({time.strftime('%Y-%m-%d')})")
    lines.append("")
    lines.append(f"- Transcripts scanned: {r['n_transcripts']}")
    lines.append(f"- User→assistant pairs: {r['n_pairs']} across {r['n_projects']} project(s)")
    lines.append(f"- Time window: last {r['window_days']} days")
    lines.append(f"- Distinctive terms tested: {r['total_terms']}")
    lines.append("")
    lines.append("## Potential CTX utility (reproducibility score)")
    lines.append("")
    lines.append(f"- **Text match rate** (terms visible in response prose): "
                 f"{fmt_rate(r['text_hits'], r['total_terms'])}")
    lines.append(f"- **Tool-use match rate** (terms visible in tool parameters): "
                 f"{fmt_rate(r['tool_hits'], r['total_terms'])}")
    lines.append(f"- **Union (either)**: {fmt_rate(r['either_hits'], r['total_terms'])}")
    lines.append(f"- **Tool-only recovery** (caught by tool-use but not text): "
                 f"{r['tool_only_hits']} terms / "
                 f"{r['tool_only_hits']/max(1,r['total_terms'])*100:.1f}pp")
    lines.append("")
    lines.append("## Per response-type")
    lines.append("")
    lines.append("| Type | pairs | terms | match rate | 95% CI |")
    lines.append("|------|:---:|:---:|:---:|:---:|")
    for rtype, d in sorted(r["by_rtype"].items(), key=lambda kv: -kv[1]["pairs"]):
        if d["terms"] == 0:
            continue
        p = d["either"] / d["terms"]
        lo, hi = wilson_ci(d["either"], d["terms"])
        lines.append(f"| {rtype} | {d['pairs']} | {d['terms']} | "
                     f"{p:.1%} | [{lo:.1%}, {hi:.1%}] |")
    lines.append("")
    lines.append("## What this measures")
    lines.append("")
    lines.append(
        "This is a **simulated** CTX utility score — we extract distinctive "
        "terms from each user prompt and check whether the assistant's "
        "response (text + tool_use params) surfaced those terms. On turns "
        "where CTX's BM25/semantic hooks WOULD have surfaced related "
        "context, this rate approximates how much of that context the "
        "assistant could plausibly have used.")
    lines.append("")
    lines.append(
        "It does NOT directly measure CTX's effect — it estimates "
        "CEILING utility on your own transcript history. Install CTX and "
        "compare against its live `utility_measured` telemetry for the "
        "actual delta.")
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    lines.append("```")
    lines.append(f"python3 ctx_validate.py --days {r['window_days']}")
    lines.append("```")
    lines.append("")
    lines.append("Source: `benchmarks/ctx_validate.py` — stdlib only, no network.")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-dir", help="Absolute path to a project root "
                    "(will look up its transcripts in ~/.claude/projects/)")
    ap.add_argument("--transcript-dir", help="Direct path to a transcripts .jsonl folder")
    ap.add_argument("--days", type=int, default=7, help="Time window in days (default 7)")
    ap.add_argument("--min-prompt-len", type=int, default=40)
    ap.add_argument("--min-response-len", type=int, default=80)
    ap.add_argument("--max-pairs", type=int, default=200)
    ap.add_argument("--out", help="Write markdown report to this path instead of stdout")
    ap.add_argument("--json", action="store_true", help="Emit raw JSON instead of markdown")
    args = ap.parse_args(argv)

    result = validate(args.project_dir, args.transcript_dir, args.days,
                      args.min_prompt_len, args.min_response_len, args.max_pairs)

    if args.json:
        payload = json.dumps(result, indent=2)
    else:
        payload = render_markdown(result)

    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote report to {args.out}", file=sys.stderr)
    else:
        print(payload)

    return 0 if not result.get("error") else 2


if __name__ == "__main__":
    sys.exit(main())
