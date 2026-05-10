"""GraphPrompt 핵심 증강 엔진

실험 결과 기반 최적 조건:
- coding:        Hierarchical + Few-shot (F) → pass@1 +24%p   (Kruskal-Wallis p=0.006)
- reasoning:     Hierarchical (E)            → faithfulness +10.2%p (p=0.000203)
- summarization: no augmentation (A)         → 구조화 역효과 확인
"""

import sys
import os

# 동일 디렉토리에서 직접 실행할 때도 import 가능하도록 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from task_detector import detect_task_type
from fewshots import get_fewshot_text

ROLES = {
    "coding": "Python 시니어 개발자",
    "reasoning": "논리적 추론 전문가",
    "summarization": "전문 요약 작가",
}

CONSTRAINTS = {
    "coding": (
        "- Python 코드로 구현\n"
        "- 함수 형태로 작성\n"
        "- 마지막 줄에 print()로 결과 출력\n"
        "- 코드만 출력"
    ),
    "reasoning": (
        "- 제공된 정보만 사용하여 단계별 추론\n"
        "- 최종 답변은 마지막 줄에 명시"
    ),
    "summarization": None,  # 증강 없음
}


def augment_prompt(
    prompt: str,
    context: str = "",
    task_type: str = "auto",
) -> dict:
    """
    프롬프트를 GraphPrompt 실험 결과 기반 최적 구조로 증강합니다.

    Returns:
        {
          "augmented_prompt": str,   # 증강된 최종 프롬프트
          "task_type": str,          # 감지/지정된 태스크 타입
          "condition": str,          # 적용된 조건 (A/E/F)
          "structure": str,          # "hierarchical" / "flat"
          "augmented": bool,         # 실제 증강 여부
        }
    """
    if task_type == "auto":
        task_type = detect_task_type(prompt)

    constraint = CONSTRAINTS.get(task_type)

    # Summarization: 증강 없음 (실험 결과 구조화 역효과)
    if task_type == "summarization" or constraint is None:
        return {
            "augmented_prompt": _build_flat(prompt, context),
            "task_type": task_type,
            "condition": "A",
            "structure": "flat",
            "augmented": False,
        }

    role = ROLES[task_type]
    use_fewshot = (task_type == "coding")

    augmented = _build_hierarchical(prompt, context, role, constraint, use_fewshot, task_type)
    condition = "F" if use_fewshot else "E"

    return {
        "augmented_prompt": augmented,
        "task_type": task_type,
        "condition": condition,
        "structure": "hierarchical",
        "augmented": True,
    }


def _build_flat(prompt: str, context: str) -> str:
    parts = []
    if context:
        parts.append(f"[컨텍스트]\n{context}")
    parts.append(prompt)
    return "\n\n".join(parts)


def _build_hierarchical(
    prompt: str,
    context: str,
    role: str,
    constraint: str,
    use_fewshot: bool,
    task_type: str,
) -> str:
    parts = [
        f"[L1: 역할] 당신은 {role}입니다.",
    ]
    if context:
        parts.append(f"[L2: 컨텍스트]\n{context}")
    parts.append(f"[L3: 제약사항]\n{constraint}")
    if use_fewshot:
        fs = get_fewshot_text(task_type)
        if fs:
            parts.append(f"[L4: 예시]\n{fs}")
    parts.append(f"[L5: 질문] {prompt}")
    return "\n\n".join(p for p in parts if p)


if __name__ == "__main__":
    import json

    # Test 1: coding
    r = augment_prompt(
        "피보나치 수열의 n번째 값을 반환하는 함수를 작성하시오.",
        task_type="coding",
    )
    print("=== CODING ===")
    print("condition:", r["condition"], "| structure:", r["structure"])
    print(r["augmented_prompt"][:300])
    print()

    # Test 2: reasoning
    r = augment_prompt(
        "철수는 영희보다 나이가 많고, 영희는 민수보다 나이가 많다. 세 명 중 가장 어린 사람은?",
        task_type="reasoning",
    )
    print("=== REASONING ===")
    print("condition:", r["condition"])
    print(r["augmented_prompt"][:200])
    print()

    # Test 3: summarization (no augmentation)
    r = augment_prompt(
        "다음 텍스트를 3문장으로 요약하시오.",
        task_type="summarization",
    )
    print("=== SUMMARIZATION (no augment) ===")
    print("augmented:", r["augmented"], "| condition:", r["condition"])
