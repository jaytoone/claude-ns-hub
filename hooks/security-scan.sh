#!/bin/bash
# security-scan.sh — PostToolUse hook (async)
# Edit/Write 후 Python 파일 보안 스캔 (HIGH severity만)
# async:true로 백그라운드 실행, 결과는 다음 턴에 systemMessage로 전달

TOOLS_VENV="$HOME/.claude/tools-venv"
BANDIT="$TOOLS_VENV/bin/bandit"

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Python 파일 아니면 스킵
[[ "$FILE_PATH" != *.py ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0
[[ ! -x "$BANDIT" ]] && exit 0

# bandit 실행 (HIGH severity + HIGH confidence만, 노이즈 최소화)
BANDIT_OUT=$("$BANDIT" "$FILE_PATH" -ll -ii -q 2>&1)
BANDIT_EXIT=$?

# 취약점 없으면 조용히 종료
[[ $BANDIT_EXIT -eq 0 ]] && exit 0

# HIGH 취약점만 필터
HIGH_ISSUES=$(echo "$BANDIT_OUT" | grep -A3 "Severity: High" | head -30)
[[ -z "$HIGH_ISSUES" ]] && exit 0

# 다음 턴에 경고 전달 (async hook → systemMessage)
MSG="[보안 스캔] $FILE_PATH 에서 HIGH 취약점 발견:
$HIGH_ISSUES

CWE 기준으로 수정이 필요합니다."

jq -n --arg msg "$MSG" '{"systemMessage": $msg}'
