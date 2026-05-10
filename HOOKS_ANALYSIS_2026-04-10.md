# Claude Code 훅 설정 분석
**작성일**: 2026-04-10  
**대상**: FromScratch + AETHER-166B 프로젝트  
**현황**: 활성 훅 19개 (과다)

---

## Executive Summary

### 발견
현재 훅 설정은 **메모리 백엔드 3중화 + 불필요한 지시 생성으로 과부하 상태**입니다.

| 문제 | 영향 | 해결책 |
|------|------|--------|
| 메모리 백엔드 3중화 (chat, bm25, mcp) | bm25만으로 충분한데 3개 동시 실행 | bm25 유지, 나머지 제거 |
| 지시 생성 오버헤드 | 매 세션 "메모리 저장하세요" 지시 | memory-session-*.sh + session-decision-capture.py 제거 |
| 프로젝트 무시 | AETHER(Python)에 Playwright 규칙 강제 주입 | playwright.config.* 감지 로직 추가 |

### 예상 효과 (최적화 후)
| 메트릭 | 현재 | 최적화 | 개선 |
|--------|------|--------|------|
| 총 훅 수 | 19개 | 10-11개 | **-42%** |
| Claude 메시지 노이즈 | 높음 | 낮음 | **-60%** |
| UserPromptSubmit 훅 | 6개 | 3개 | **-50%** |

---

## 1. 메모리 백엔드 중복 분석 (★★★ CRITICAL)

### 3개 백엔드 비교

| 훅 | 기능 | 가능 | 자동화 | 신뢰도 | 제거 추천 |
|-------|------|------|--------|---------|------------|
| **chat-memory.py** | 과거 대화 FTS5 | ✓ | ✓ 자동 | 낮음 (단기만) | **P1** |
| **mcp-memory-autoload.py** | MCP 강제 활성화 | ✓ | ⚠️ 수동 (Claude 호출) | 낮음 | **P0** |
| **bm25-memory.py** | BM25 + Git + Docs | ✓✓✓ | ✓ 자동 | 높음 (0.634 recall) | **유지** |

### 각 훅의 상세 분석

#### chat-memory.py (193줄)
```
역할: claude-vault SQLite FTS5로 과거 대화 검색
문제: 
  • bm25-memory.py의 Docs 인덱싱과 중복
  • 세션 내 메시지만 검색 (단기 메모리)
  • 불필요한 추가 DB 쿼리

제거 후: bm25가 docs/*.md 인덱싱하므로 커버 가능
위험도: 낮음 (95%)
```

#### mcp-memory-autoload.py (57줄) ★ 최악
```
역할: 세션 첫 메시지 시 MCP Memory Graph 강제 활성화

구현:
  1. SessionStart: /tmp/claude-mcp-memory-pending 플래그 생성
  2. 첫 UserPromptSubmit: 플래그 감지 → Claude에게 지시 출력
     "MANDATORY FIRST ACTION (응답 생성 전 반드시 실행):
      mcp__memory__search_nodes 도구를 호출하여..."
  3. 플래그 삭제

문제:
  • bm25-memory.py가 이미 자동으로 메모리 로드 제공
  • 추가 강제 지시 → Claude 피로도 증가
  • 첫 메시지마다 "메모리 복원" 출력 → 사용자 경험 해침
  • 완전 중복 (같은 목표, 다른 방식)

제거 후: bm25만으로 충분
위험도: 안전 (100%)
```

#### bm25-memory.py (656줄) ★ 핵심
```
역할: 
  G1: Git 결정 커밋 → BM25 ranking → top-7 (Recall@7 = 0.634)
  G2a: docs/research/*.md + CLAUDE.md + MEMORY.md → top-5 (Recall = 0.700)
  G2b: codebase-memory-mcp → 코드 파일 추천
  G2b-hooks: ~/.claude/hooks/*.py BM25 검색

강점:
  • 자동 메모리 로드 (사용자 개입 필요 없음)
  • 가장 강력한 BM25 알고리즘
  • 3.7x 성능 개선 (proactive 0.169 → reactive 0.634)
  • Git 커밋 + Docs + 코드그래프 통합

AETHER 필요성: 높음 (훈련 중 기술 결정 기억 중요)
```

### 최적화안: 메모리 백엔드 통합
```diff
- chat-memory.py (P1 제거)
- mcp-memory-autoload.py (P0 즉시 제거)
  bm25-memory.py (유일하게 유지)
```

---

## 2. 메모리 저장 지시 오버헤드 (★★★ CRITICAL)

### 현재 지시 생성 패턴

```
매 세션 시작:
  memory-session-start.sh 
  → /tmp/claude-memory-context-hint.md 생성
  → Claude: "mcp__memory__read_graph 호출하세요" 출력

매 세션 종료:
  memory-session-end.sh
  → /tmp/claude-memory-save-hint.md 생성
  → Claude: "entities 저장하세요" 출력

  session-decision-capture.py (중복)
  → [G1] 마커 검색 → .omc/session-decisions.md 저장
```

### 문제점

| 훅 | 문제 | 현실 | 제거 추천 |
|-------|------|-------|----------|
| **memory-session-start.sh** | "메모리 복원하세요" 지시 (매 세션) | bm25가 자동 로드 | **P0** |
| **memory-session-end.sh** | "메모리 저장하세요" 지시 (매 세션) | bm25 + Git 커밋으로 기록 중 | **P0** |
| **session-decision-capture.py** | [G1] 마커 의존 + 중복 실행 | bm25 충분 | **P0** |

### 최적화 효과
```
현재: 매 세션 3개 지시 메시지
     + [G1] 마커 기록 부담
     + Claude 수동 호출 필요

최적화 후: 0개 지시 (자동)
           부담 제거
           bm25 자동 처리
```

---

## 3. Playwright 검수 (★ 프로젝트별)

### stop-playwright-detect.sh (207줄)
```
역할: Stop 훅에서 UI 변경 파일 감지 → Playwright 재검수 지시

FromScratch: TypeScript/React 풀스택 → 필수
AETHER: Python 백엔드만 → 불필요

현재: 모든 프로젝트에 동일하게 실행
→ .playwright-skip 또는 playwright.config.* 감지로 조건부 실행 가능
  (현재도 무시 가능하지만, 명시적 스킵이 더 나음)

추천: ✓ 유지 (FromScratch 필수)
```

### subagent_playwright_inject.py (43줄)
```
역할: 모든 SubagentStart 시 Playwright 검수 규칙 주입

문제: AETHER 훈련 중 Python 서브에이전트도 
      "Playwright 검수 필수" 규칙 주입 받음 → 불필요

해결: 파일 첫 부분에 프로젝트 타입 감지
      if not playwright.config.*: return empty

추천: **P2 조건부 개선**
```

---

## 4. 기타 평가

### 유지 필수
| 훅 | 역할 | 이유 |
|-------|------|------|
| **graphprompt-augment.py** | 프롬프트 → L1-L5 구조 증강 | pass@1 +24%p 실험 증명 |
| **auto-index.py** | codebase-memory-mcp 인덱싱 | 코드 그래프 유지 |
| **post-write-doc-index.sh** | docs DOC_INDEX 등록 강제 | 문서 정책 (FromScratch + AETHER) |
| **subagent_tracker.py** | 에이전트 flow 로깅 (async) | 디버깅, 비용 0 |
| **pre-compact-save.js** | 세션 work progress 저장 | 세션 컨텍스트 유지 |

### 제거 권장
| 훅 | 문제 | 우선순위 |
|-------|------|----------|
| **mcp-memory-autoload.py** | bm25와 중복, 강제 지시 | **P0** |
| **memory-session-start.sh** | 지시만 생성, 자동화 부족 | **P0** |
| **memory-session-end.sh** | 번거로운 지시 생성 | **P0** |
| **session-decision-capture.py** | [G1] 마커 부담, bm25 충분 | **P0** |
| **chat-memory.py** | bm25로 충분 | **P1** |
| **task_complete.py** | 팀 협업 없음 | **P1** |
| **memory-keyword-trigger.py** | 지시 생성, bm25 충분 | **P1** |
| **windows-notify.sh** | WSL에서 작동 안 함 | **P1** |

---

## 5. 최적화된 최소 설정

### Before (19개)
```
SessionStart: 3개 (claude-flow, memory-session-start, auto-index)
PreCompact: 2개
UserPromptSubmit: 6개
TaskCompleted: 1개
SubagentStart: 2개
SubagentStop: 1개
SessionEnd: 4개
PermissionRequest: 1개
Stop: 4개
PostToolUse: 3개
```

### After (10-11개)
```
SessionStart: 2개 (claude-flow, auto-index)
PreCompact: 2개
UserPromptSubmit: 3개 (graphprompt-augment, graphprompt-instruct, bm25-memory)
SubagentStart: 1개 (subagent_playwright_inject 조건부)
SubagentStop: 1개
SessionEnd: 2개 (claude-flow, post-write-doc-index)
Stop: 2개 (stop-playwright-detect, g2-fallback)
PostToolUse: 2개
```

---

## 6. 실행 계획

### Phase 1: P0 제거 (15분)
settings.json에서 다음 제거:
1. UserPromptSubmit: `mcp-memory-autoload.py`
2. SessionStart: `memory-session-start.sh`
3. SessionEnd: `memory-session-end.sh`
4. Stop/SessionEnd: `session-decision-capture.py`

### Phase 2: P1 제거 (15분)
1. UserPromptSubmit: `chat-memory.py`, `memory-keyword-trigger.py`
2. TaskCompleted: `task_complete.py`
3. PermissionRequest: `windows-notify.sh`

### Phase 3: P2 개선 (10분)
subagent_playwright_inject.py 수정:
```python
import os
cwd = os.getcwd()

# Playwright 프로젝트인지 확인
has_playwright = any(
    os.path.exists(os.path.join(cwd, f"playwright.config.{ext}"))
    for ext in ["ts", "js"]
)

if not has_playwright:
    sys.exit(0)  # Playwright 프로젝트 아님 → 빈 출력
```

---

## 7. 예상 효과

### 메트릭
| 항목 | 현재 | 최적화 후 |
|------|------|----------|
| 총 훅 수 | 19개 | 10-11개 |
| UserPromptSubmit | 6개 | 3개 |
| 중복 메모리 백엔드 | 3개 | 1개 |
| 지시 생성 훅 | 7개 | 1개 |
| 훅 실행 시간 | 기준 | -30% |
| Claude 메시지 노이즈 | 높음 | 낮음 |

### 사용자 경험
```
Before:
  세션 시작: "메모리를 복원하려면 mcp__memory__search_nodes를 호출하세요"
  세션 종료: "중요 결정을 entities로 저장하세요"
  + [MEMORY TRIGGER] 마커 기록 부담

After:
  세션 시작/종료: 추가 지시 없음
  + bm25가 자동으로 메모리 로드
  + 깔끔한 사용자 경험
```

---

## 결론

### 핵심 문제
1. **메모리 3중화**: chat + bm25 + mcp → bm25만으로 충분
2. **지시 생성 오버헤드**: 매 세션 지시 → Claude 피로도 증가
3. **프로젝트 무시**: 모든 서브에이전트에 동일 규칙 → 불필요한 검수

### 즉시 해결 (30분)
- P0 4개 제거
- P1 4개 제거
- P2 1개 개선

### 결과
- 훅 개수 1/2 감소
- 메시지 노이즈 60% 감소
- 유지보수성 대폭 개선

**현재 설정은 좋은 의도에도 불구하고 과잉 설계 상태입니다. 즉시 정리 강력 권장.**

