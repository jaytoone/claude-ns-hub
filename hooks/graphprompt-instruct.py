#!/usr/bin/env python3
"""
GraphPrompt Instruct Hook — UserPromptSubmit
역할: 키워드 분류가 불확실한 경우 Claude가 직접 판단하도록 지시 주입

graphprompt-augment.py 가 명시적 증강을 주입했다면 그걸 우선 사용.
주입 없는 경우(키워드 미감지) → Claude가 내부적으로 판단+증강.
"""
import json
import sys
import os

EMPTY = json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": ""
    }
})

SKIP_PREFIXES = ["/"]
SKIP_TAGS = ["[raw]"]


def should_skip(prompt: str) -> bool:
    p = prompt.strip()
    if len(p) < 10:
        return True
    if any(p.startswith(x) for x in SKIP_PREFIXES):
        return True
    if any(t in p.lower() for t in SKIP_TAGS):
        return True
    return False


INSTRUCTION = """<graphprompt_meta>
[GraphPrompt 자동 적용 지시]
위 graphprompt 블록이 없거나 질문 유형이 불명확한 경우, 아래 기준으로 내부 적용:
- 코딩/프로그래밍 질문 → L1-L5 Hierarchical+FewShot 구조로 재구성 후 답변 (pass@1 +24%p)
- 논리적 추론/다단계 질문 → L1-L5 Hierarchical 구조로 재구성 후 답변 (faithfulness +10.2%p)
- 요약/정리 요청 → 그냥 답변 (구조화 역효과 확인)
증강된 프롬프트를 먼저 출력한 뒤 답변하세요.
</graphprompt_meta>"""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print(EMPTY)
        return

    prompt = data.get("prompt", "")

    if should_skip(prompt):
        print(EMPTY)
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": INSTRUCTION
        }
    }))


if __name__ == "__main__":
    main()
