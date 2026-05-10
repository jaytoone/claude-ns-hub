#!/bin/bash
# post-edit-ts-check.sh
# PostToolUse/Edit|Write 후 TypeScript 파일 빠른 구문 검사
#
# 동작:
#   1. 편집된 파일이 .ts/.tsx인지 확인 → 아니면 즉시 스킵
#   2. /tmp 경로 스킵
#   3. node --check로 JS 구문 검사 (빠름, ~50ms)
#   4. 오류 발견 시 Claude에게 경고 출력 (exit 2)
#
# async: true → Claude 흐름 차단 없이 백그라운드 실행, 다음 턴에 결과 전달
#
# Version: 1.0.0 (2026-02-25)

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null)

# TypeScript 파일이 아니면 스킵
if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.tsx ]]; then
  exit 0
fi

# /tmp 경로 스킵
if [[ "$FILE_PATH" == /tmp/* ]] || [[ "$FILE_PATH" == /var/tmp/* ]]; then
  exit 0
fi

# 파일 존재 확인
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# ── node --check: JS 구문 체크 (TypeScript 구문은 무시, 기본 구문만) ──
# TypeScript 전용 구문(interface, type, :type 등)은 node가 모름 → 일단 스킵
# 대신 괄호/중괄호 균형 휴리스틱 체크
OPEN_PAREN=$(grep -o '(' "$FILE_PATH" 2>/dev/null | wc -l)
CLOSE_PAREN=$(grep -o ')' "$FILE_PATH" 2>/dev/null | wc -l)
OPEN_BRACE=$(grep -o '{' "$FILE_PATH" 2>/dev/null | wc -l)
CLOSE_BRACE=$(grep -o '}' "$FILE_PATH" 2>/dev/null | wc -l)

PAREN_DIFF=$(( OPEN_PAREN - CLOSE_PAREN ))
BRACE_DIFF=$(( OPEN_BRACE - CLOSE_BRACE ))

# 임계값: 5 이상 차이나면 의심
ISSUES=""

if [[ ${PAREN_DIFF#-} -gt 5 ]]; then
  ISSUES+="소괄호 불균형: open=${OPEN_PAREN}, close=${CLOSE_PAREN} (차이 ${PAREN_DIFF})\n"
fi

if [[ ${BRACE_DIFF#-} -gt 5 ]]; then
  ISSUES+="중괄호 불균형: open=${OPEN_BRACE}, close=${CLOSE_BRACE} (차이 ${BRACE_DIFF})\n"
fi

# tsconfig.json 있는 프로젝트는 npx tsc --noEmit 단일 파일 체크
PROJECT_DIR=$(dirname "$FILE_PATH")
MAX_DEPTH=5
DEPTH=0
TSCONFIG_DIR=""
SEARCH_DIR="$PROJECT_DIR"

while [[ "$SEARCH_DIR" != "/" && $DEPTH -lt $MAX_DEPTH ]]; do
  if [[ -f "$SEARCH_DIR/tsconfig.json" ]]; then
    TSCONFIG_DIR="$SEARCH_DIR"
    break
  fi
  SEARCH_DIR=$(dirname "$SEARCH_DIR")
  DEPTH=$((DEPTH + 1))
done

if [[ -n "$TSCONFIG_DIR" ]]; then
  # tsc --noEmit --skipLibCheck (빠른 체크)
  TS_RESULT=$(cd "$TSCONFIG_DIR" && npx tsc --noEmit --skipLibCheck 2>&1 | grep "error TS" | grep -F "$FILE_PATH" | head -5)
  if [[ -n "$TS_RESULT" ]]; then
    ISSUES+="TypeScript 컴파일 오류:\n${TS_RESULT}\n"
  fi
fi

if [[ -n "$ISSUES" ]]; then
  FILENAME=$(basename "$FILE_PATH")
  printf "⚠️ [PostToolUse] ${FILENAME} 편집 후 잠재적 오류 감지:\n${ISSUES}\n파일: ${FILE_PATH}\n→ Phase 3A quality 영향: TypeScript 에러 시 base 0.3으로 감소" >&2
  exit 2
fi

exit 0
