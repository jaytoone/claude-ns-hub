#!/usr/bin/env python3
"""
Stream Router — UserPromptSubmit Hook
역할: 프롬프트 키워드로 스트림 감지 → 에이전트 라우팅 힌트 주입
"""
import json, sys, os, subprocess

def get_git_status():
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--porcelain"],
            capture_output=True, text=True, timeout=3
        )
        return result.stdout.strip()[:200] or "없음"
    except Exception:
        return "N/A"

def detect_stream(prompt: str) -> str:
    p = prompt.lower()

    stream4 = ["검수", "검토", "리뷰", "확인해줘", "제대로 됐어", "verify", "review", "check", "validate"]
    stream1 = ["조사", "리서치", "파악", "탐색", "찾아줘", "어디있어", "어떻게 돼", "research", "find", "investigate", "explore", "analyze", "파일 보여", "읽어"]
    stream2 = ["계획", "설계", "구조", "어떻게 할까", "방법", "plan", "design", "architecture", "approach"]
    stream3 = ["구현", "만들어", "작성", "추가", "수정", "고쳐", "build", "implement", "create", "write", "fix", "update", "add"]
    stream3_deep = ["전체", "end-to-end", "자율", "복잡한", "대규모", "리팩토링", "멀티파일", "autonomous", "refactor", "complex", "large-scale"]

    # 우선순위: stream4 > stream1 > stream2 > stream3_deep > stream3
    if any(k in p for k in stream4):
        return "stream4"
    if any(k in p for k in stream1):
        return "stream1"
    if any(k in p for k in stream2):
        return "stream2"
    # deep 키워드 단독으로도 stream3_deep 트리거
    if any(k in p for k in stream3_deep):
        return "stream3_deep"
    if any(k in p for k in stream3):
        return "stream3"
    return "auto"

ROUTING = {
    "auto":       "복잡도 자동 판단",
    "stream1":    "research-explore 에이전트 우선 (haiku, 탐색/리서치 전담)",
    "stream2":    "ops-planner 에이전트 (opus, 계획·TaskCreate DAG)",
    "stream3":    "dev-executor 에이전트 (sonnet, 구현 전담)",
    "stream3_deep": "dev-deep-executor 에이전트 (opus, 복잡한 멀티파일 end-to-end 구현)",
    "stream4":    "review-verifier 에이전트 (opus, 검수 전담)",
}

def main():
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "")
    session_id = data.get("session_id", "unknown")[:8]
    cwd = os.path.basename(os.getcwd())
    stream = detect_stream(prompt)

    DELEGATE = {
        "stream1":    'Task(subagent_type="research-explore", model="haiku") 로 위임. 직접 탐색 금지.',
        "stream2":    'Task(subagent_type="ops-planner", model="opus") 로 위임. 직접 계획 금지.',
        "stream3":    'Task(subagent_type="dev-executor") 로 위임. 직접 구현 금지.',
        "stream3_deep": 'Task(subagent_type="dev-deep-executor", model="opus") 로 위임. 직접 구현 금지.',
        "stream4":    'Task(subagent_type="review-verifier", model="opus") 로 위임. 직접 검수 금지.',
        "auto":       "",
    }
    delegate_instruction = DELEGATE.get(stream, "")

    context = f"""<stream_routing>
session: {session_id} | project: {cwd}
git: {get_git_status()}
감지 스트림: {stream} — {ROUTING[stream]}
{f"[MANDATORY] {delegate_instruction}" if delegate_instruction else ""}
에이전트 직접 호출:
  research-explore  (haiku) — Task(subagent_type="research-explore")
  ops-planner       (opus)  — Task(subagent_type="ops-planner")
  dev-executor      (sonnet)— Task(subagent_type="dev-executor")
  dev-deep-executor (opus)  — Task(subagent_type="dev-deep-executor")
  review-verifier   (opus)  — Task(subagent_type="review-verifier")
</stream_routing>"""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context
        }
    }))

if __name__ == "__main__":
    main()
