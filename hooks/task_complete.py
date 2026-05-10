#!/usr/bin/env python3
"""
Task Complete — TaskCompleted Hook
역할: 태스크 완료 시 자동 검수 트리거 힌트 주입
"""
import json, sys

def main():
    data = json.load(sys.stdin)
    subject = data.get("subject", "태스크")
    task_id = data.get("taskId", "?")

    context = f"""<task_completed>
완료: [{task_id}] {subject}
→ 검수: "review-verifier 에이전트로 검수해줘"
→ 추가 구현: "dev-executor 에이전트로 [작업]"
→ 문서화: "ops-planner 에이전트로 정리해줘"
</task_completed>"""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "TaskCompleted",
            "additionalContext": context
        }
    }))

if __name__ == "__main__":
    main()
