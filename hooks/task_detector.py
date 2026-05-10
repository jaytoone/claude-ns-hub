"""키워드 기반 태스크 타입 자동 감지"""

CODING_KEYWORDS = [
    "def ", "function", "implement", "코드", "구현", "함수",
    "algorithm", "class ", "python", "작성",
]
SUMMARIZATION_KEYWORDS = [
    "요약", "summarize", "summary", "정리해", "핵심", "summarization",
]


def detect_task_type(prompt: str) -> str:
    """
    Returns: 'coding', 'summarization', 'reasoning'
    """
    lower = prompt.lower()
    coding_score = sum(1 for kw in CODING_KEYWORDS if kw in lower)
    summary_score = sum(1 for kw in SUMMARIZATION_KEYWORDS if kw in lower)

    if coding_score > summary_score and coding_score >= 1:
        return "coding"
    if summary_score > coding_score and summary_score >= 1:
        return "summarization"
    return "reasoning"
