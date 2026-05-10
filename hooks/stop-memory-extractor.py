#!/usr/bin/env python3
"""
stop-memory-extractor.py — Stop hook
At session end, analyze the transcript with an LLM and suggest decisions
worth writing to MEMORY.md.

Flow:
  1. Extract recent assistant turns from the transcript
  2. Ask Haiku: "Are there any decisions from this session worth remembering?"
  3. If yes, emit a suggestion via additionalContext (not a forced write —
     Claude makes the final call)
"""
import json
import os
import sys
import re
from pathlib import Path

MAX_TRANSCRIPT_CHARS = 8000   # max transcript length sent to the LLM
MIN_SESSION_TURNS = 3          # skip overly short sessions
MODEL = "claude-haiku-4-5-20251001"  # fast and cheap
MEMORY_TRIGGER_PHRASES = [
    "completed", "implemented", "decision", "decided", "selected", "chose",
    "abandon", "abandoned", "rollback", "reverted", "kill", "killed",
    "achieved", "finalized", "introduced", "removed", "changed",
    "new goal", "iter", "goal", "fixed", "resolved",
]


def get_memory_path(cwd: str) -> Path:
    safe = cwd.replace("/", "-").replace(" ", "-")
    return Path.home() / ".claude" / "projects" / safe / "memory" / "MEMORY.md"


def extract_transcript_summary(transcript_path: str) -> tuple[str, int]:
    """Extract recent messages from the transcript. Supports Claude Code .jsonl format. Returns (text, turn_count)."""
    if not os.path.exists(transcript_path):
        return "", 0

    turns = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                    entry_type = d.get("type", "")

                    if entry_type == "user":
                        msg = d.get("message", {})
                        if isinstance(msg, dict):
                            content = msg.get("content", "")
                            if isinstance(content, str) and content.strip():
                                turns.append(f"[user] {content[:200]}")
                            elif isinstance(content, list):
                                for c in content:
                                    if isinstance(c, dict) and c.get("type") == "text":
                                        t = c.get("text", "")
                                        if t.strip():
                                            turns.append(f"[user] {t[:200]}")
                                            break

                    elif entry_type == "assistant":
                        msg = d.get("message", {})
                        if isinstance(msg, dict):
                            content = msg.get("content", [])
                            if isinstance(content, list):
                                for c in content:
                                    if isinstance(c, dict) and c.get("type") == "text":
                                        t = c.get("text", "")
                                        if t.strip():
                                            turns.append(f"[assistant] {t[:300]}")
                                            break
                except Exception:
                    continue
    except Exception:
        return "", 0

    # Only keep the last 20 turns
    recent = turns[-20:]
    return "\n".join(recent), len(turns)


def has_decision_signal(text: str) -> bool:
    """Fast pre-filter: skip the LLM call when no decision keywords are present."""
    lower = text.lower()
    return any(p in lower for p in MEMORY_TRIGGER_PHRASES)


def ask_llm(transcript_text: str, memory_path: str) -> str | None:
    """Use `claude -p` (built-in LLM) to extract memorable decisions. Returns None when there is nothing to remember."""
    import subprocess
    import tempfile

    current_memory = ""
    mp = Path(memory_path)
    if mp.exists():
        current_memory = mp.read_text(encoding="utf-8")[:1500]

    prompt = f"""Below is the recent conversation from a Claude Code session.

<session>
{transcript_text[:MAX_TRANSCRIPT_CHARS]}
</session>

<current_memory>
{current_memory}
</current_memory>

Question: Are there any **important decisions or changes from this session
that should be remembered for future sessions**?

Worth remembering:
- Rollbacks or changes to technical decisions (e.g. "decided to keep verb synonyms")
- Measured metrics or achieved goals (e.g. "eval variance reached 0pp")
- New goals set (e.g. "omc goal: stabilize eval")
- Core features that were implemented (e.g. "cache layer implemented with corpus_hash")
- Structural limitations discovered (e.g. "found root cause of hook not registering")

Not worth remembering:
- Temporary debugging or error-fix intermediate steps
- Simple file reads / lookups
- Intermediate process (only final results matter)

Format:
- If worth remembering: output 1-3 lines, each "DECISION: [one-line summary]"
- If nothing: output just "SKIP"

Answer:"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--bare"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip()
        if not output or output.upper().startswith("SKIP"):
            return None
        # Filter to only DECISION: lines
        lines = [l for l in output.split("\n") if l.strip().startswith("DECISION:")]
        return "\n".join(lines) if lines else None
    except Exception:
        return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        sys.exit(0)

    cwd = os.getcwd()
    memory_path = str(get_memory_path(cwd))

    transcript_text, turn_count = extract_transcript_summary(transcript_path)
    if turn_count < MIN_SESSION_TURNS:
        sys.exit(0)  # session too short

    # Pre-filter: skip LLM call when no decision signal is present
    if not has_decision_signal(transcript_text):
        sys.exit(0)

    # Extract decisions via LLM
    decisions = ask_llm(transcript_text, memory_path)
    if not decisions:
        sys.exit(0)

    # Emit as additionalContext so Claude picks it up in the next response
    print("[MEMORY EXTRACTOR] Decisions worth remembering were detected in this session.")
    print("Extracted decisions:")
    for line in decisions.split("\n"):
        if line.strip():
            print(f"  {line}")
    print(f"MEMORY.md path: {memory_path}")
    print()
    print("Optional action: Leave it to Claude to decide whether to add these to MEMORY.md.")
    print("(Not a forced write — Claude updates manually on the next session based on this context.)")

    sys.exit(0)


if __name__ == "__main__":
    main()
