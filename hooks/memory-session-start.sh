#!/usr/bin/env bash
# memory-session-start.sh
# SessionStart hook: memory-context-hint.md 힌트 파일 생성
# Claude가 세션 시작 시 이 파일을 읽어 mcp__memory__read_graph 호출하도록 유도

set -euo pipefail

HINT_FILE="$HOME/.claude/memory-context-hint.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
PROJECT_DIR="${PWD:-unknown}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
MEMORY_FILE="$HOME/.claude/memory-graphs/$PROJECT_NAME/memory.jsonl"

cat > "$HINT_FILE" <<EOF
# Memory MCP - 세션 시작 컨텍스트 복원 요청
_생성 시각: ${TIMESTAMP}_
_프로젝트: ${PROJECT_DIR}_

## [자동 지시] SessionStart 컨텍스트 복원

이 파일이 존재하는 경우, 세션 시작 시 다음을 실행하십시오:

1. \`mcp__memory__read_graph\` 도구를 호출하여 전체 Knowledge Graph를 읽습니다.
2. 반환된 entities / relations 중 현재 프로젝트와 관련된 항목을 요약합니다.
3. 요약 내용을 컨텍스트에 주입합니다 (사용자에게 간략히 보고).
4. 이 힌트 파일을 삭제합니다: \`rm $HINT_FILE\`

### 복원 명령 (Claude가 실행할 내용)
\`\`\`
mcp__memory__read_graph({})
\`\`\`

### 결과 처리 지침
- entities: 프로젝트명, 기술 결정, 미해결 문제 위주로 요약
- relations: 인과관계 / 의존관계 중심으로 파악
- 현재 프로젝트 경로(${PROJECT_DIR})와 관련된 항목 우선 제시

### Memory 파일 경로 (프로젝트 격리)
- 프로젝트: ${PROJECT_NAME}
- Memory 파일: ${MEMORY_FILE}
EOF

# Inject Conceptual paradigm + project nodes into hint
PARADIGM_FILE="$HOME/.claude/skills/conceptual/state/paradigm.json"
NODES_FILE="$HOME/.claude/skills/conceptual/state/nodes/${PROJECT_NAME}.jsonl"

if [ -f "$PARADIGM_FILE" ] && [ -s "$PARADIGM_FILE" ]; then
    PARADIGM_CONTENT=$(cat "$PARADIGM_FILE")
    cat >> "$HINT_FILE" <<EOF

### Conceptual Paradigm State (auto-loaded, apply silently)
\`\`\`json
${PARADIGM_CONTENT}
\`\`\`
EOF
fi

if [ -f "$NODES_FILE" ] && [ -s "$NODES_FILE" ]; then
    NODES_CONTENT=$(tail -10 "$NODES_FILE")
    cat >> "$HINT_FILE" <<EOF

### Conceptual Memory Nodes — ${PROJECT_NAME} (last 10)
\`\`\`
${NODES_CONTENT}
\`\`\`
EOF
fi

echo "[memory-session-start] hint file written: $HINT_FILE"

# mcp-memory-autoload.py 트리거 플래그 생성 (첫 UserPromptSubmit에서 소비됨)
touch /tmp/claude-mcp-memory-pending
echo "[memory-session-start] mcp-memory-pending flag set"

# 팝업 슬롯 stale 정리 (celi 재시작 후 dead PID 잔류 방지)
LOCK_DIR="/tmp/claude-notify-stack"
if [ -d "$LOCK_DIR" ]; then
    for i in 0 1 2 3 4 5 6 7 8 9; do
        pid_file="$LOCK_DIR/slot_$i/pid"
        if [ -d "$LOCK_DIR/slot_$i" ]; then
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file" 2>/dev/null)
                if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
                    rm -f "$pid_file"
                    rmdir "$LOCK_DIR/slot_$i" 2>/dev/null
                fi
            else
                rmdir "$LOCK_DIR/slot_$i" 2>/dev/null
            fi
        fi
    done
    echo "[memory-session-start] notify slots cleaned"
fi

exit 0
