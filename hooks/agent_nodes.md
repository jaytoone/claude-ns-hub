# Agent Nodes v3.3
_적응형 멀티 오케스트레이션 — DIRECT / PIPELINE / SWARM_
_버전: 2026-03-03 | thin orchestrator — 도구 상세는 각 스킬 SKILL.md 참조_
_백업: agent_nodes_v3_backup_20260302.md_


## 스킬 위치

| 스킬 | 파일 |
|------|------|
| `Skill("node1-ask")`    | `~/.claude/skills/node1-ask/SKILL.md`      |
| `Skill("node2-debate")` | `~/.claude/skills/node2-debate/SKILL.md`   |
| `Skill("node3-paper")`  | `~/.claude/skills/node3-paper/SKILL.md`    |
| `Skill("node4-result")` | `~/.claude/skills/node4-result/SKILL.md`   |
| `Skill("node5-verify")` | `~/.claude/skills/node5-verify/SKILL.md`   |

> 도구 매트릭스·MCP 카탈로그·ToolSearch 시나리오 → 각 스킬 SKILL.md 참조

---

## 필수 규칙

1. **도구 사용 전**: `ToolSearch`로 deferred tools 로드 필수
2. **작업 추적**: trajectory-start → step → end (모든 복잡도)
3. **품질 기록**: node4-result에서 `trajectory-step` 필수
4. **메트릭스 수집**: node1-ask + node5-verify에서 `hooks_metrics` 필수
5. **패턴 저장**: node5-verify에서 `hooks_intelligence_pattern-store` (성공=task-routing, 실패=failure-case)
6. **LATS 종료 기준**: quality ≤ 0.5 → 최대 2회 재실행 → 2회 연속 실패 → Node 2 재기획
7. **메모리**: 중요한 기술 결정만 `memory_store`

---

## 모든 요청: Node 1 먼저 (예외 없음)

```
Skill("node1-ask")  →  복잡도 판단  →  아래 3개 모드 중 하나 자동 선택
```

---

## 모드 A: DIRECT (LOW)

**TodoWrite 없음.** 최소 오버헤드 — 단일 에이전트 직접 실행.

```
Skill("node1-ask")
  → code-index 조사 (현황 파악)
  → 직접 구현/응답
```

---

## 모드 B: PIPELINE (MEDIUM)

**계획 → 구현 → 검수** 순차 파이프라인. Node 4에서 병렬 블록 실행.

```
// 1. 태스크 등록 (의존성 포함)
n2 = TaskCreate({ subject: "Node 2 DEBATE",  activeForm: "설계 토론 중" })
n3 = TaskCreate({ subject: "Node 3 PAPER",   activeForm: "PAPER 저장 중" })
n4 = TaskCreate({ subject: "Node 4 RESULT",  activeForm: "구현 중" })
n5 = TaskCreate({ subject: "Node 5 VERIFY",  activeForm: "검수 중" })
TaskUpdate(n3.id, { addBlockedBy: [n2.id] })  // N3는 N2 완료 후
TaskUpdate(n4.id, { addBlockedBy: [n3.id] })  // N4는 N3 완료 후
TaskUpdate(n5.id, { addBlockedBy: [n4.id] })  // N5는 N4 완료 후

// 2. 순차 실행 (스킵 시 TaskUpdate status="deleted")
TaskUpdate(n2.id, { status: "in_progress" })
Skill("node2-debate")                          // 3-에이전트 병렬 토론 → PAPER 초안
TaskUpdate(n2.id, { status: "completed" })

// Node 3 스킵 조건: 일회성 작업 / 영구 문서화 불필요
// → TaskUpdate(n3.id, { status: "deleted" })
TaskUpdate(n3.id, { status: "in_progress" })
Skill("node3-paper")                           // PAPER 파일 저장
TaskUpdate(n3.id, { status: "completed" })

TaskUpdate(n4.id, { status: "in_progress" })
Skill("node4-result")                          // PARALLEL 블록 → Task 병렬 호출
TaskUpdate(n4.id, { status: "completed" })

// Node 5 스킵 조건: 코드 변경 없음 (문서·설정만)
// → TaskUpdate(n5.id, { status: "deleted" })
TaskUpdate(n5.id, { status: "in_progress" })
Skill("node5-verify")                          // Q1~Q4 검수
TaskUpdate(n5.id, { status: "completed" })
```

**스킵 조건 요약**

| 노드 | `deleted` 처리 조건 |
|------|-------------------|
| Node 3 PAPER  | 일회성 작업 / 영구 문서화 불필요 |
| Node 5 VERIFY | 코드 변경 없음 (문서·설정만 수정) |

---

## 모드 C: SWARM (HIGH)

**병렬 탐색 + 자율 구현.** 계획과 구현이 동시 진행.

```
1. Node 1에서 독립 작업 스트림 N개 식별 (2~4개)

2. 스트림별 TodoWrite 동적 생성:
   TodoWrite([
     { id: "stream-1", content: "[스트림 1: 설명]", status: "pending" },
     { id: "stream-2", content: "[스트림 2: 설명]", status: "pending" },
     ...
     { id: "synth",   content: "합성 → PAPER 확정", status: "pending" },
     { id: "verify",  content: "Node 5 VERIFY",     status: "pending" },
   ])

3. 단일 응답 블록에서 스트림 동시 실행:
   Task(stream-1, run_in_background=True, isolation="worktree",
     prompt="[스트림 1 범위] 탐색·구현·테스트를 자율적으로 진행.
     ⚠️ 깊이 제한: 서브 Task는 1레벨까지만 허용. 서브에이전트에서 추가 Task 호출 금지.")
   Task(stream-2, run_in_background=True, isolation="worktree", ...)
   ...

4. 모든 스트림 완료 대기 → 합성 → Skill("node3-paper") → Skill("node5-verify")
```

> ⚠️ 스트림 간 파일 의존성 높으면 PIPELINE으로 강등

---