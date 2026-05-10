#!/usr/bin/env python3
"""
SubagentStart Hook — Playwright 검수 규칙 자동 주입 v1.0.0
모든 서브에이전트가 시작될 때 Playwright 검수 절차를 additionalContext로 주입.
stop hook(stop-playwright-detect.sh)의 프로액티브 파트너.
"""
import json, sys

PLAYWRIGHT_RULE = """
[MANDATORY AGENT RULE — Playwright Verification]
구현/리팩토링/버그수정 작업을 완료한 후 반드시 아래 순서를 따를 것:

1. TypeScript 체크: npx tsc --noEmit (0 errors 확인)
2. Playwright E2E 검수 (session-4 우선, SingletonLock 회피):
   - 개발 서버 실행 확인 (localhost:3000)
   - 변경된 UI 컴포넌트/페이지 직접 탐색 및 클릭
   - 탭 전환, 패널 렌더링, 버튼 동작 확인
   - 브라우저 콘솔 에러 0 확인
3. 위 2단계 모두 PASS → 그 후에만 커밋 여부를 사용자에게 질문

절대 금지:
- Playwright 검수 없이 커밋 여부를 먼저 묻는 것
- TypeScript 체크만 하고 Playwright 생략하는 것
- "빌드 성공" 만으로 검수 완료로 간주하는 것
"""

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    # additionalContext를 stdout으로 출력 → Claude Code가 서브에이전트에 주입
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": PLAYWRIGHT_RULE.strip()
        }
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
