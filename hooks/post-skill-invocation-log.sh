#!/bin/bash
# Post-Skill 호출 로거 — 각 Skill() 호출을 기록
# PostToolUse hook: matcher = "Skill"
# stdin JSON 구조: {"tool_name":"Skill","tool_input":{"skill":"node1-ask"},...}

LOG_FILE="${SKILL_LOG_FILE:-/tmp/skill-invocations.log}"

# stdin에서 JSON 파싱 (python3 없으면 grep 폴백)
INPUT=$(cat)

SKILL_NAME=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(ti.get('skill', ti.get('args', 'unknown')))
except Exception as e:
    print('parse-error')
" 2>/dev/null)

SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

echo "${TIMESTAMP} [${SESSION_ID:0:8}] SKILL_CALLED: ${SKILL_NAME}" >> "$LOG_FILE"
