#!/usr/bin/env python3
"""
GraphPrompt Augment Hook — UserPromptSubmit
역할: 프롬프트 자동 감지 → 최적 구조로 증강 → additionalContext 주입

스킵 조건:
- 10자 미만 (짧은 명령어)
- / 로 시작 (슬래시 커맨드)
- ? 로 끝나는 짧은 질문
- summarization 감지 (증강 효과 없음)
- [raw] 태그 포함 (유저 명시 스킵)
"""
import json
import sys
import os

AUGMENTOR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AUGMENTOR_DIR)

EMPTY = json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": ""
    }
})


def should_skip(prompt: str) -> bool:
    p = prompt.strip()
    if len(p) < 10:
        return True
    if p.startswith("/"):
        return True
    if "[raw]" in p.lower():
        return True
    # 짧은 질문 (한글 포함 30자 미만 + 물음표)
    if len(p) < 30 and p.endswith("?"):
        return True
    return False


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

    try:
        from augmentor import augment_prompt
        result = augment_prompt(prompt)

        # summarization 또는 증강 없음 → 스킵
        if not result.get("augmented"):
            print(EMPTY)
            return

        task = result["task_type"]
        condition = result["condition"]
        augmented = result["augmented_prompt"]

        EVIDENCE = {
            "F": "coding pass@1 +24%p (p=0.000126)",
            "E": "multihop faithfulness +10.2%p (p=0.005)",
        }
        evidence = EVIDENCE.get(condition, "")

        context = (
            f"<graphprompt>\n"
            f"[GraphPrompt 자동 증강] 태스크: {task} | 조건: {condition} | 근거: {evidence}\n"
            f"아래 증강된 프롬프트를 출력하고 이를 기반으로 답변하세요:\n"
            f"────────────────────────────────────────────────\n"
            f"{augmented}\n"
            f"</graphprompt>"
        )

        # stderr → Claude Code UI에 즉시 표시
        print(f"[GraphPrompt] {task} → 조건 {condition} ({evidence})", file=sys.stderr)

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context
            }
        }))

    except Exception:
        print(EMPTY)


if __name__ == "__main__":
    main()
