#!/bin/bash
# test-failure-analysis.sh — PostToolUseFailure hook
# Bash 명령 실패 시 traceback 분석 힌트 제공
# pytest/python 실행 실패에만 작동

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
ERROR=$(echo "$INPUT" | jq -r '.error // ""')

# pytest 또는 python 실행 실패만 처리
if ! echo "$COMMAND" | grep -qE "pytest|python.*\.py|python3.*\.py"; then
  exit 0
fi

# 에러 없으면 스킵
[[ -z "$ERROR" ]] && exit 0

# 에러 유형 분류
HINT=""
if echo "$ERROR" | grep -q "ModuleNotFoundError\|ImportError"; then
  HINT="ImportError 감지: 패키지 설치 또는 경로 확인 필요 (pip install / sys.path 확인)"
elif echo "$ERROR" | grep -q "TypeError"; then
  HINT="TypeError 감지: 인수 타입/개수 확인, 함수 시그니처 확인"
elif echo "$ERROR" | grep -q "AttributeError"; then
  HINT="AttributeError 감지: 객체 속성/메서드명 확인, None 체크 필요"
elif echo "$ERROR" | grep -q "KeyError"; then
  HINT="KeyError 감지: dict key 존재 여부 확인, .get() 사용 고려"
elif echo "$ERROR" | grep -q "AssertionError\|assert"; then
  HINT="Assertion 실패: 테스트 기댓값과 실제값 비교 - traceback의 assert 라인 확인"
elif echo "$ERROR" | grep -q "SyntaxError\|IndentationError"; then
  HINT="구문 오류: 들여쓰기/괄호/콜론 확인"
elif echo "$ERROR" | grep -q "FAILED\|ERROR"; then
  HINT="테스트 실패: traceback의 파일명/라인번호로 실패 지점 확인"
fi

# additionalContext로 분석 힌트 전달
CTX="[오류 분석]
명령: $COMMAND
오류 유형: ${HINT:-'일반 오류'}
오류 내용:
$(echo "$ERROR" | head -20)

위 오류를 분석하여 수정하세요."

jq -n --arg ctx "$CTX" '{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": $ctx
  }
}'
