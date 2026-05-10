#!/bin/bash
# UserPromptSubmit hook: 사용자 의도 + git 스냅샷 저장
#
# 역할: 사용자 요청을 프로젝트+세션별 격리된 파일에 저장
#       + 응답 시작 시점의 git 상태 스냅샷 저장
#       → Stop agent가 "이번 응답에서 변경된 것만" 비교 가능
#
# 파일 명명 규칙:
#   /tmp/claude-intent-{project_hash}-{session_id_short}.txt  (세션별 격리)
#   /tmp/claude-git-snapshot-{project_hash}-{session_id_short}.txt
#
# Version: 1.3.0 (2026-02-20) - session_id 기반 세션별 파일 격리 (다중 세션 중복 체크 방지)

INPUT=$(cat)

# session_id + prompt 추출
SESSION_AND_PROMPT=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    sid = d.get('session_id', '').strip()[:12]
    prompt = d.get('prompt', '').strip()
    print(sid)
    print(prompt)
except:
    print('')
    print('')
" 2>/dev/null)

SESSION_ID=$(echo "$SESSION_AND_PROMPT" | head -1)
PROMPT=$(echo "$SESSION_AND_PROMPT" | tail -n +2)

# 짧은 메타 승인 건너뜀 (1-2자 승인어만 스킵)
# 임계값 3: "ㄱㄱ"(2), "ok"(2), "ㅇㅇ"(2), "네"(1), "응"(1) → 스킵
# "yes"(3), "수정해"(3), "버그 수정"(5) → 저장
# Stop agent가 SHORT META 여부를 최종 판단
PROMPT_LEN=${#PROMPT}
if [ "$PROMPT_LEN" -lt 3 ]; then
    exit 0
fi

# ── 프로젝트별 격리 ──────────────────────────────────────────
GIT_ROOT=$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
GIT_ROOT_HASH=$(echo "$GIT_ROOT" | md5sum | cut -d' ' -f1 | head -c8)
GIT_HEAD=$(git -C "$GIT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")

# ── 세션별 파일 경로 결정 ─────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    # 세션별 격리 (다중 세션 동시 작업 지원)
    SESSION_SHORT="${SESSION_ID:0:8}"
    INTENT_FILE="/tmp/claude-intent-${GIT_ROOT_HASH}-${SESSION_SHORT}.txt"
    SNAPSHOT_FILE="/tmp/claude-git-snapshot-${GIT_ROOT_HASH}-${SESSION_SHORT}.txt"
else
    # fallback: 세션 ID 없으면 프로젝트별 단일 파일
    INTENT_FILE="/tmp/claude-intent-${GIT_ROOT_HASH}.txt"
    SNAPSHOT_FILE="/tmp/claude-git-snapshot-${GIT_ROOT_HASH}.txt"
fi

# ── 의도 저장 ─────────────────────────────────────────────────
{
  echo "# PROJECT_PATH: $GIT_ROOT"
  echo "# PROJECT_HASH: $GIT_ROOT_HASH"
  echo "# SESSION_ID: ${SESSION_ID:-none}"
  echo "# TIMESTAMP: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "# GIT_HASH: $GIT_HEAD"
  echo "---"
  echo "$PROMPT"
} > "$INTENT_FILE"

# ── git 스냅샷 저장 (응답 시작 시점의 변경 파일 목록) ─────────
# Stop agent가 이 목록에 있는 파일은 "이미 수정 중이었던 것"으로 간주
git -C "$GIT_ROOT" diff HEAD --name-only 2>/dev/null > "$SNAPSHOT_FILE"
git -C "$GIT_ROOT" ls-files --others --exclude-standard 2>/dev/null >> "$SNAPSHOT_FILE"

# 히스토리 로그 (session_id 포함)
echo "$(date '+%Y-%m-%d %H:%M:%S') [${GIT_ROOT_HASH}${SESSION_SHORT:+-$SESSION_SHORT}]: ${PROMPT:0:100}" >> /tmp/claude-intent-history.log

exit 0
