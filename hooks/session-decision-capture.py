#!/usr/bin/env python3
"""
session-decision-capture.py — Stop hook
자연어 패턴 기반 결정 감지 (마커 의존 제거).

전략:
  1. 전체 트랜스크립트 스캔 (마지막 메시지만 아님)
  2. 한국어 + 영어 커밋먼트 패턴 감지
  3. 발화자 교차 확인 (제안 → 수락 페어)
  4. .omc/session-decisions.md에 추가
"""
import json, sys, os, re
from datetime import datetime
from pathlib import Path


# ── 강한 결정 패턴 (신뢰도 0.9+) ──────────────────────────────
KO_STRONG = [
    "진행하겠습니다", "하겠습니다", "하기로 했", "결정했",
    "삭제하겠", "제거하겠", "비활성화하겠", "적용하겠",
    "동의합니다", "확인됐", "확정됐", "완료됐",
]
KO_MEDIUM = [
    "진행합니다", "하기로", "결론은", "방향은",
    "이렇게 가겠", "이걸로 가겠",
]
EN_STRONG = re.compile(
    r"\b(I\'ll|we\'ll|will|confirmed|approved|agreed|decided|going with|ship it|let\'s proceed|remove|disable|delete)\b",
    re.IGNORECASE
)

# ── 거부 패턴 (필터링용) ───────────────────────────────────────
KO_REJECT = ["아니오", "안 됩니다", "못하겠", "않겠습니다", "하지 않겠"]
EN_REJECT = re.compile(r"\b(no|won\'t|can\'t|disagree|reject|not going)\b", re.IGNORECASE)

# ── 노이즈 제외 패턴 ──────────────────────────────────────────
SKIP_PATTERNS = [
    r"```",            # 코드 블록 내부
    r"^\s*#",         # 주석
    r"example",       # 예시 설명
    r"예를 들어",
]


def extract_text(content):
    """content가 str 또는 list[block]일 때 텍스트 추출."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def is_noisy(line):
    for pat in SKIP_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return True
    return False


def score_line(line, role):
    """결정 신뢰도 점수 반환. 0이면 결정 아님."""
    if is_noisy(line):
        return 0.0

    # 거부 패턴 → 무시
    if any(r in line for r in KO_REJECT):
        return 0.0
    if EN_REJECT.search(line):
        return 0.0

    score = 0.0

    # 한국어 강한 패턴
    for pat in KO_STRONG:
        if pat in line:
            score = max(score, 0.9)
            break

    # 한국어 중간 패턴
    if score == 0.0:
        for pat in KO_MEDIUM:
            if pat in line:
                score = max(score, 0.7)
                break

    # 영어 패턴
    if EN_STRONG.search(line):
        score = max(score, 0.85)

    # 사용자 발화면 가중치 +0.05
    if role == "user" and score > 0:
        score = min(1.0, score + 0.05)

    return score


def summarize_decision(line, max_len=120):
    """결정 문장을 간결하게 요약 (앞부분 트런케이션)."""
    line = line.strip()
    if len(line) > max_len:
        line = line[:max_len].rstrip() + "…"
    return line


def extract_decisions(transcript, min_score=0.75):
    """
    전체 트랜스크립트에서 결정 추출.
    반환: list of (role, text, score)
    """
    decisions = []
    prev_role = None
    prev_was_proposal = False  # 직전 메시지가 제안/질문이었는지

    PROPOSAL_SIGNALS = [
        "할까요", "하겠어요", "진행할까요", "어떨까요", "할까",
        "should we", "shall we", "let's", "do you want", "would you like",
        "제거할까", "삭제할까", "비활성화할까",
    ]

    for msg in transcript:
        role = msg.get("role", "")
        if role not in ("user", "assistant"):
            prev_role = role
            continue

        text = extract_text(msg.get("content", ""))
        if not text:
            continue

        # 발화자 교차 확인 (제안 → 수락 페어)
        cross_speaker_bonus = 0.0
        if prev_was_proposal and role != prev_role:
            cross_speaker_bonus = 0.1  # 교차 발화 시 신뢰도 보너스

        # 줄별 스캔
        for line in text.split("\n"):
            line = line.strip()
            if len(line) < 5:
                continue
            s = score_line(line, role)
            s = min(1.0, s + cross_speaker_bonus)
            if s >= min_score:
                decisions.append((role, summarize_decision(line), round(s, 2)))

        # 다음 반복을 위해 제안 여부 기록
        prev_was_proposal = any(sig in text for sig in PROPOSAL_SIGNALS)
        prev_role = role

    # 중복 제거 (동일 텍스트)
    seen = set()
    unique = []
    for role, text, score in decisions:
        if text not in seen:
            seen.add(text)
            unique.append((role, text, score))

    return unique


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    transcript = data.get("transcript") or data.get("messages") or []
    if not transcript:
        return

    decisions = extract_decisions(transcript)
    if not decisions:
        return

    # 프로젝트 루트 탐색
    cwd = data.get("cwd") or os.getcwd()
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True
        )
        project_root = r.stdout.strip() if r.returncode == 0 else cwd
    except Exception:
        project_root = cwd

    omc_dir = Path(project_root) / ".omc"
    omc_dir.mkdir(exist_ok=True)
    decisions_file = omc_dir / "session-decisions.md"

    existing = decisions_file.read_text() if decisions_file.exists() else ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    for role, text, score in decisions:
        if text not in existing:
            lines.append(f"> {now} [{role}|{score:.0%}]: {text}")

    if lines:
        with open(decisions_file, "a") as f:
            f.write("\n".join(lines) + "\n")
        print(f"[decision-capture] {len(lines)}개 결정 저장 → {decisions_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
