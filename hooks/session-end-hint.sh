#!/bin/bash
# SessionEnd: MEMORY.md 업데이트 힌트 파일 생성
# Compact 힌트가 이미 있으면 덮어쓰기 스킵 (PreCompact 정보 보존)

HINT="$HOME/.claude/.memory-update-hint.md"

if [ -f "$HINT" ] && grep -q "Compact" "$HINT" 2>/dev/null; then
    echo '[memory] Compact hint exists — session-end skip'
    exit 0
fi

printf '# MEMORY.md 업데이트 힌트\n**세션 종료**: %s\n\n세션이 정상 종료됐습니다. 다음 세션 시작 시 MEMORY.md를 현재 프로젝트 상태로 업데이트하세요.\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" \
  > "$HINT" 2>/dev/null

echo '[memory] Session-end hint saved'
