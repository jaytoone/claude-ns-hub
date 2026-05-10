#!/usr/bin/env python3
"""
prompt-mission-tracker.py — UserPromptSubmit hook
Detects task/mission prompts → injects instruction to create milestone + cron.

Triggers when prompt contains task keywords or /live /fix /build etc.
Claude then: creates milestone in hub NS, creates CronCreate to monitor until done.
"""
import json, re, sys
from pathlib import Path

data = {}
try:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    pass

prompt = data.get("prompt", "").strip()
cwd = data.get("cwd", "")
session_id = data.get("session_id", "")[:8]

if not prompt:
    sys.exit(0)

# Task signal detection
TASK_PATTERNS = [
    r"\blive\b.*-i\b", r"/live\b", r"/fix\b", r"/build\b",
    r"\bimplement\b", r"\bbuild\b", r"\bcreate\b", r"\brefactor\b",
    r"\badd\b.{5,}", r"\bfix\b.{5,}", r"\bupdate\b.{5,}",
    r"\bwrite\b.{5,}", r"\bdevelop\b", r"\bsetup\b", r"\bintegrate\b",
]

is_task = any(re.search(p, prompt, re.I) for p in TASK_PATTERNS)
# Skip if too short (< 15 chars) or looks like a question
is_question = prompt.endswith("?") or re.match(r"^(what|why|how|when|where|who|is|are|can|do|does|did)\b", prompt, re.I)
is_task = is_task and len(prompt) > 15 and not is_question

if not is_task:
    sys.exit(0)

# Find project ID from CWD
def get_proj_id(cwd: str) -> str | None:
    DIR_MAP = {"Moat":"MOAT","CTX":"CTX","FromScratch":"FromScratch",
               "FRWP":"FRWP","HugwartsBanana":"HugwartsBanana","AIKB":"AIKB",
               "Clone":"Clone","EI":"EI","FreeOS":"FreeOS","Ameva":"Ameva"}
    for part in reversed(Path(cwd).parts):
        if part in DIR_MAP:
            return DIR_MAP[part]
        # Auto-scan
        hub_proj = Path.home() / f".claude/hub/projects/{part}"
        if hub_proj.exists():
            return part
    return None

proj_id = get_proj_id(cwd)
if not proj_id:
    sys.exit(0)

# Truncate prompt to milestone title
title = re.sub(r'\s+', ' ', prompt[:70]).strip()
if len(prompt) > 70:
    title += "…"

ctx = (
    f"[MISSION TRACKER] This prompt looks like a task. Before starting:\n"
    f"1. Create a milestone in hub: POST http://100.119.82.4:9000/api/northstar/{proj_id}/milestones "
    f"with {{\"text\": \"{title}\", \"layer\": 0}}\n"
    f"2. Note the milestone ID returned (e.g. M8)\n"
    f"3. Create CronCreate(cron='*/15 * * * *', "
    f"prompt='Check {proj_id}/MX in ~/.claude/hub/projects/{proj_id}/completion-log.jsonl. "
    f"If found: PATCH http://100.119.82.4:9000/api/northstar/{proj_id}/milestones/MX "
    f"with status=pending_confirmation, then CronDelete this job.', recurring=True)\n"
    f"4. When task is complete this session, write to completion-log.jsonl\n"
    f"Then proceed with the task."
)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": ctx
    }
}))
