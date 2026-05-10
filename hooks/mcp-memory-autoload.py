#!/usr/bin/env python3
"""
mcp-memory-autoload.py
UserPromptSubmit Hook: 세션 첫 메시지에서 mcp__memory__ 강제 활성화

동작:
1. SessionStart 시 memory-session-start.sh가 /tmp/claude-mcp-memory-pending 플래그 생성
2. 첫 UserPromptSubmit에서 플래그 감지 → MANDATORY 지시 주입 → 플래그 삭제
3. 이후 메시지에서는 플래그 없음 → 조용히 종료
"""
import json
import sys
import os
from pathlib import Path

FLAG_FILE = "/tmp/claude-mcp-memory-pending"


def get_project_name() -> str:
    cwd = os.getcwd()
    return os.path.basename(cwd)


def main():
    # stdin 읽기 (hook 입력)
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # 플래그 파일 존재 여부 확인
    if not Path(FLAG_FILE).exists():
        sys.exit(0)

    # 플래그 소비 (삭제) — 첫 메시지에서만 동작
    try:
        os.unlink(FLAG_FILE)
    except OSError:
        sys.exit(0)

    project = get_project_name()

    # MANDATORY 지시 주입 — Claude가 첫 응답 전에 반드시 실행
    print("[MCP MEMORY AUTOLOAD] 세션 첫 메시지 감지 — 메모리 복원 필요")
    print()
    print("MANDATORY FIRST ACTION (응답 생성 전 반드시 실행):")
    print(f"  mcp__memory__search_nodes 도구를 호출하여 '{project}' 관련 과거 결정을 복원하세요.")
    print("  호출 형식: mcp__memory__search_nodes({{\"query\": \"{project} decisions\"}})")
    print("  결과가 없으면 조용히 넘어가도 됩니다.")
    print()
    print("이 지시는 세션 첫 메시지에서만 1회 실행됩니다.")

    sys.exit(0)


if __name__ == "__main__":
    main()
