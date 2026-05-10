#!/bin/bash
# post-write-doc-index.sh
# Write/Edit 도구로 docs/*.md 파일 저장 시 DOC_INDEX.md 등록 여부 강제 확인
#
# 동작:
#   1. Write 또는 Edit 도구로 docs/*.md (DOC_INDEX.md 제외) 저장 감지
#   2. 해당 파일이 docs/DOC_INDEX.md에 등록되어 있는지 확인
#   3. 미등록 시 → blocking feedback으로 Claude에게 추가 지시
#
# Version: 1.0.0 (2026-03-03)

INPUT=$(cat)

# 도구명 파싱
TOOL_NAME=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('tool_name', ''))
" 2>/dev/null)

# Write/Edit 이외는 무시
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

# 파일 경로 파싱 (Write: tool_input.file_path, Edit: tool_input.file_path)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('file_path', ''))
" 2>/dev/null)

# docs/**/*.md 파일이고 DOC_INDEX.md / PAPER_*.md 가 아닌 경우만 체크 (서브폴더 포함)
if [[ ! "$FILE_PATH" =~ /docs/.+\.md$ ]]; then
  exit 0
fi

FILENAME=$(basename "$FILE_PATH")

# DOC_INDEX.md 자체는 제외
if [[ "$FILENAME" == "DOC_INDEX.md" ]]; then
  exit 0
fi

# docs/DOC_INDEX.md 경로 결정 — 프로젝트 루트 docs/ 고정 (서브폴더 무관)
# PROJECT_ROOT 환경변수 우선, 없으면 git rev-parse로 탐색
GIT_ROOT=$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null)
PROJ_ROOT="${PROJECT_ROOT:-$GIT_ROOT}"

# Fallback: git root 없을 때 상위 디렉토리를 순회하며 docs/DOC_INDEX.md 탐색
if [ -z "$PROJ_ROOT" ]; then
  DIR=$(dirname "$FILE_PATH")
  while [ "$DIR" != "/" ]; do
    if [ -f "$DIR/docs/DOC_INDEX.md" ]; then
      PROJ_ROOT="$DIR"
      break
    fi
    DIR=$(dirname "$DIR")
  done
fi

DOC_INDEX="${PROJ_ROOT}/docs/DOC_INDEX.md"

# 상대 경로로 표시 (메시지용) — PROJ_ROOT 기준
REL_PATH="${FILE_PATH#${PROJ_ROOT}/}"

# DOC_INDEX.md가 없는 경우
if [ ! -f "$DOC_INDEX" ]; then
  echo "⚠️  docs/DOC_INDEX.md 가 존재하지 않습니다."
  echo "    파일: ${REL_PATH:-$FILENAME}"
  echo "    조치: docs/DOC_INDEX.md 생성 후 위 파일을 상단 테이블에 추가하세요."
  exit 2
fi

# 파일명 또는 상대경로가 DOC_INDEX.md에 등록되어 있는지 확인
if ! grep -qE "($FILENAME|${REL_PATH//\//\\/})" "$DOC_INDEX" 2>/dev/null; then
  echo "⚠️  docs/DOC_INDEX.md 업데이트 필요"
  echo "    파일: ${REL_PATH:-$FILENAME}"
  echo "    조치: docs/DOC_INDEX.md 상단 테이블에 다음 형식으로 한 줄 추가하세요:"
  echo "    | YYYYMMDD | ${REL_PATH:-$FILENAME} | 한줄 요약 (30자 이내) |"
  exit 2
fi

exit 0
