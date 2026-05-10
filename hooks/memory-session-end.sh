#!/usr/bin/env bash
# memory-session-end.sh
# SessionEnd / PreCompact hook: memory-save-hint.md 힌트 파일 생성
# Claude가 세션 종료 전 핵심 entities를 mcp__memory__create_entities로 저장하도록 유도

set -euo pipefail

HINT_FILE="$HOME/.claude/memory-save-hint.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
PROJECT_DIR="${PWD:-unknown}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
MEMORY_FILE="$HOME/.claude/memory-graphs/$PROJECT_NAME/memory.jsonl"
GIT_BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "no-git")

cat > "$HINT_FILE" <<EOF
# Memory MCP - 세션 종료 저장 요청
_생성 시각: ${TIMESTAMP}_
_프로젝트: ${PROJECT_DIR}_
_브랜치: ${GIT_BRANCH}_

## [자동 지시] SessionEnd/PreCompact 핵심 내용 저장

이 파일이 존재하는 경우, 세션 종료 전 다음을 실행하십시오:

1. 현재 세션에서 다룬 **중요 기술 결정**, **미해결 문제**, **재사용 가능한 패턴**을 식별합니다.
2. \`mcp__memory__create_entities\` 도구로 entities를 저장합니다.
3. \`mcp__memory__create_relations\` 도구로 entities 간 관계를 저장합니다.
4. 이 힌트 파일을 삭제합니다: \`rm $HINT_FILE\`

### 저장 기준 (선택적 저장 원칙)
- ✅ 저장: 중요 기술 결정, 미해결 문제 (P0/P1), 재사용 가능한 패턴, 환경 함정
- ❌ 저장 안 함: 일회성 작업 계획, 완료된 작업 상세, trajectory

### Entity 템플릿 예시
\`\`\`json
{
  "entities": [
    {
      "name": "프로젝트명-결정사항-${TIMESTAMP:0:10}",
      "entityType": "TechnicalDecision",
      "observations": ["결정 내용 요약", "근거", "영향 범위"]
    },
    {
      "name": "프로젝트명-미해결-${TIMESTAMP:0:10}",
      "entityType": "OpenIssue",
      "observations": ["문제 설명", "우선순위", "현재 상태"]
    }
  ]
}
\`\`\`

### 현재 세션 메타데이터
- 프로젝트: ${PROJECT_DIR}
- 브랜치: ${GIT_BRANCH}
- 시각: ${TIMESTAMP}
- Memory 파일: ${MEMORY_FILE}
EOF

echo "[memory-session-end] hint file written: $HINT_FILE"
exit 0
