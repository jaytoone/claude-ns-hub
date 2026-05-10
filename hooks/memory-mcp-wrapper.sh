#!/usr/bin/env bash
# memory-mcp-wrapper.sh
# PWD 기준 프로젝트 이름 감지 → MEMORY_FILE_PATH 설정 → MCP 실행

PROJECT_DIR="${PWD:-$HOME}"
PROJECT_NAME=$(basename "$PROJECT_DIR")
MEMORY_DIR="$HOME/.claude/memory-graphs"
mkdir -p "$MEMORY_DIR/$PROJECT_NAME"
export MEMORY_FILE_PATH="$MEMORY_DIR/$PROJECT_NAME/memory.jsonl"
exec npx -y @modelcontextprotocol/server-memory
