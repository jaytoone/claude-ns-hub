"""Few-shot 예시 저장소

실험 조건 F (Hierarchical + Few-shot) 에 사용되는 예시들.
coding 태스크에만 적용 (p0-prompt-eval 실험 결과 기반).
"""

CODING_FEWSHOTS = """[예시 1]
문제: 리스트의 최댓값을 반환하는 함수를 작성하시오.
입력: [3, 1, 4, 1, 5, 9]
출력: 9
답변:
def solution(nums):
    return max(nums)
print(solution([3, 1, 4, 1, 5, 9]))

[예시 2]
문제: 문자열을 뒤집는 함수를 작성하시오.
입력: "hello"
출력: "olleh"
답변:
def solution(s):
    return s[::-1]
print(solution("hello"))"""


def get_fewshot_text(task_type: str) -> str:
    """
    태스크 타입에 맞는 few-shot 예시 텍스트를 반환합니다.
    해당 없으면 빈 문자열 반환.
    """
    if task_type == "coding":
        return CODING_FEWSHOTS
    return ""
