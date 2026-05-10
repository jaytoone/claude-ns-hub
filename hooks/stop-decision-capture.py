#!/usr/bin/env python3
"""
stop-decision-capture.py — Stop hook (Pattern B: queue file architecture)

At session end, analyze the transcript with local keyword patterns and
save candidate decisions into .pending-decisions.json.

On the next session's UserPromptSubmit, bm25-memory.py reads this file
and passes it to Claude as additionalContext, so Claude can decide
whether to update MEMORY.md.

Characteristics:
  - No LLM calls (100% local, ~10-30ms)
  - Pulls decision patterns from the last 5 assistant turns
  - BM25 dedup against recent MEMORY.md content
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MIN_SESSION_TURNS = 3     # skip overly short sessions
MAX_CANDIDATES = 5        # max decisions saved
MAX_CONTEXT_CHARS = 150   # context window around each match

# ── Decision detection patterns ─────────────────────────────────────
# Patterns that indicate a completed decision in assistant messages.
DECISION_PATTERNS = [
    # Technical decision completed
    (r"(rollback|reverted|revert|roll\s*back)\s*(to|decision|planned|confirmed|done)", "rollback"),
    (r"(iter|iteration)\s*\d+\s*(completed?|complete|success|done)", "iter_complete"),
    (r"(cache|caching)\s*(implementation|implemented|completed|added|introduced|designed)", "cache_impl"),
    (r"(eval|evaluation|benchmark)\s*(stabilized|fixed|frozen|finalized|completed)", "eval_stable"),
    (r"(recall|score|metric|performance)\s*[\d.]+\s*(achieved|fixed|frozen|finalized|completed)", "metric_achieved"),
    # omc goal change
    (r"/live\s+\w+", "goal_change"),
    (r"(goal|new\s*goal)\s*(change|changed|switched|new|:)\s*.{3,40}", "goal_change"),
    # Project state
    (r"(project|item|service)\s*(kill|killed|stopped|shut\s*down|dropped|abandoned)", "project_kill"),
    (r"(kill)\s*(confirmed|completed|done)", "project_kill"),
    # Strategy / approach decision
    (r"(channel|strategy|method|approach)\s*(change|changed|switched|decided|finalized)\s*.{0,30}", "strategy"),
    (r"(excluded|exclusion|skip\s*decision|decided\s*to\s*exclude)", "exclusion"),
    (r"(no\s+more|stop(ping)?|will\s+not)\s*(follow[- ]up|contact|DM|message|outreach)", "exclusion"),
    # Metric achieved (G1 Recall, eval score, etc.)
    (r"Recall@\d+\s*[=:]\s*[\d.]+", "metric"),
    (r"score\s*[=:]\s*[\d.]+", "metric"),
    (r"R@\d+\s*[=:]\s*[\d.]+", "metric"),
    (r"variance\s*[=:]\s*[\d.]+\s*pp", "variance"),
    # Implementation completed
    (r"(implemented|completed|achieved|fixed|resolved|done)", "impl_complete"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), tag) for p, tag in DECISION_PATTERNS]


def get_paths(cwd: str):
    """Return (pending-decisions.json path, MEMORY.md path) for a given cwd."""
    slug = cwd.replace("/", "-")
    memory_dir = Path.home() / ".claude" / "projects" / slug / "memory"
    return (
        memory_dir / ".pending-decisions.json",
        memory_dir / "MEMORY.md",
    )


def parse_transcript(transcript_path: str):
    """
    Extract the most recent assistant messages (up to 5) from a Claude Code
    .jsonl transcript.
    Returns a list of (role, text) tuples and the total turn count.
    """
    if not os.path.exists(transcript_path):
        return [], 0

    turns = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                    entry_type = d.get("type", "")

                    if entry_type == "user":
                        msg = d.get("message", {})
                        content = msg.get("content", "")
                        if isinstance(content, str) and content.strip():
                            turns.append(("user", content[:300]))
                        elif isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "text":
                                    t = c.get("text", "").strip()
                                    if t:
                                        turns.append(("user", t[:300]))
                                        break

                    elif entry_type == "assistant":
                        msg = d.get("message", {})
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "text":
                                    t = c.get("text", "").strip()
                                    if t:
                                        turns.append(("assistant", t[:500]))
                                        break
                except Exception:
                    continue
    except Exception:
        return [], 0

    return turns, len(turns)


# Suppress false positives produced by omc-live / hook internal processing text.
# If the surrounding context contains one of these markers, the match is treated
# as internal noise rather than a real decision.
_INTERNAL_NOISE_PATTERNS = re.compile(
    r'Flag parsing|args\s*=\s*["\']|PRE-LOOP|GoalTree|'
    r'\*\*NEW GOAL\*\*|Step\s+\d+.*Initialize|'
    r'WAVE1|wave1_plan|omc-live iter|autopilot_summary',
    re.IGNORECASE
)


def is_internal_noise(context: str) -> bool:
    """Return True when the context looks like an omc-live / hook internal false positive."""
    return bool(_INTERNAL_NOISE_PATTERNS.search(context))


def extract_decisions(turns):
    """
    Extract candidate decisions from assistant messages.
    Scans all messages in reverse (newest first) so it works regardless of
    session length.
    Returns a list of {"text": str, "context": str, "tag": str}.
    """
    # All assistant messages in reverse order (newest first)
    all_assistant = [text for role, text in reversed(turns) if role == "assistant"]

    candidates = []
    seen_contexts = set()

    # Newest first, cap at 50 messages scanned (performance limit)
    for text in all_assistant[:50]:
        for pat, tag in COMPILED:
            for m in pat.finditer(text):
                start = max(0, m.start() - 30)
                end = min(len(text), m.end() + MAX_CONTEXT_CHARS)
                context = text[start:end].strip()
                context = re.sub(r'\s+', ' ', context)

                # Filter out omc-live internal processing noise
                if is_internal_noise(context):
                    continue

                # Dedup near-identical contexts
                context_key = context[:60].lower()
                if context_key in seen_contexts:
                    continue
                seen_contexts.add(context_key)

                # Skip overly short matches
                if len(m.group(0)) < 3:
                    continue

                candidates.append({
                    "text": m.group(0)[:80],
                    "context": context[:MAX_CONTEXT_CHARS],
                    "tag": tag,
                })
                if len(candidates) >= MAX_CANDIDATES * 2:
                    break
            if len(candidates) >= MAX_CANDIDATES * 2:
                break

    # Sort by tag priority: metric > iter_complete > eval_stable > others
    TAG_PRIORITY = {
        "metric": 0, "iter_complete": 1, "eval_stable": 2,
        "metric_achieved": 3, "impl_complete": 4,
        "goal_change": 5, "rollback": 6,
        "cache_impl": 7, "variance": 8,
        "project_kill": 9, "strategy": 10, "exclusion": 11,
    }
    candidates.sort(key=lambda x: TAG_PRIORITY.get(x["tag"], 99))
    return candidates[:MAX_CANDIDATES]


def is_duplicate_of_memory(context: str, memory_path: Path) -> bool:
    """Return True when MEMORY.md already contains something similar (simple substring check)."""
    if not memory_path.exists():
        return False
    try:
        memory_text = memory_path.read_text(encoding="utf-8").lower()
        # Compare number + keyword pairs extracted from the context.
        numbers = re.findall(r'[\d.]+', context)
        key_words = re.findall(r'[a-zA-Z]{3,}', context.lower())
        if numbers and key_words:
            for num in numbers[:2]:
                for kw in key_words[:3]:
                    if num in memory_text and kw in memory_text:
                        return True
    except Exception:
        pass
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        sys.exit(0)

    cwd = os.getcwd()
    pending_path, memory_path = get_paths(cwd)

    turns, turn_count = parse_transcript(transcript_path)
    if turn_count < MIN_SESSION_TURNS:
        sys.exit(0)

    candidates = extract_decisions(turns)
    if not candidates:
        sys.exit(0)

    # Drop items that MEMORY.md already covers
    unique = [
        c for c in candidates
        if not is_duplicate_of_memory(c["context"], memory_path)
    ]
    if not unique:
        sys.exit(0)

    # Save pending-decisions.json
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "cwd": cwd,
        "turn_count": turn_count,
        "decisions": unique,
    }
    try:
        pending_path.parent.mkdir(parents=True, exist_ok=True)
        pending_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception:
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
