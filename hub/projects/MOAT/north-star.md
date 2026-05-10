---
category: Engineering
connections:
- CTX
- FromScratch
- HugwartsBanana
current: '60'
deadline: '2026-08-31'
id: MOAT
layer: 1
links: ''
log:
- date: '2026-05-09'
  text: '6ff2aff init: Moat project'
- date: '2026-05-10'
  text: '6ff2aff init: Moat project'
- date: '2026-05-10'
  text: 'b2640d9 config: update playwright hook to use verifyPlanUrl inline verification;
    6ff2aff init: Moat project'
metric: Hub dashboard completeness score (%)
milestones:
- done: true
  id: M1
  layer: 0
  parent_id: null
  status: done
  text: All 14 E2E invariant checks passing (health × 4, tab × 4, dark mode × 4, ns_nodes,
    no_errors)
- done: true
  id: M3
  layer: 0
  parent_id: null
  status: done
  text: Milestone system fully functional — 3-state toggle, auto-ack, confirm-delete,
    delete+confirm
- done: true
  id: M4
  layer: 0
  parent_id: null
  status: done
  text: Stop hook E2E verify — hub/verify.py 14-check runs on every session end
- claude_ack: 2026-05-10T17:34
  done: false
  id: M8
  layer: 0
  parent_id: null
  text: milestone 설계서 making skills needed, very 체계적이고 크론의 생명 주기를 고려한 , 여러가지 문제 발생
    성을 고려한 스타를 향한 마일스톤(크론) 설게서 를 만들어내는 스킬이 필요함
  user_added_at: 2026-05-10T17:30
- claude_ack: 2026-05-10T18:51
  done: true
  done_at: 2026-05-10T18:51
  id: M9
  layer: 0
  parent_id: null
  queued_at: 2026-05-10T18:29
  status: done
  text: 마일스톤 생성시 기본 적으로 보여지는 new milestone 텍스트를 회색의 배경 글자로 설정하여 입력시 방해받지 않도록 설정한다.
  user_added_at: 2026-05-10T17:42
- claude_ack: 2026-05-10T18:52
  done: true
  done_at: 2026-05-10T18:52
  id: M10
  layer: 0
  parent_id: null
  queued_at: 2026-05-10T18:29
  status: done
  text: Okr pane 이 굳이 필요할까 싶고, frwp 처럼 복수의 노스스타를 가지는 경우에 대해서 페이지 네이션을 마일스톤 차원이 아닌
    현재 왼쪽에 패널 (즉 노스 스타 / okr / milestone ) 을 포함한 페이지 네이션이 되어야할것이다. 즉 스타 별로 프로그래스 아크가
    보여지게 되겠지 .
  user_added_at: 2026-05-10T17:44
- claude_ack: 2026-05-10T18:46
  done: false
  id: M11
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-10T18:46
  status: pending
  text: Spec docs 도 현재 오른 패널에 보여지는데 왼쪽 패널에 통합가능는게 좋을것 (어차피 버튼 으로 존재하니까 ) -> 노트 패널은
    왜 필요한지 잘모르겠다. -> 현재 디테일 스타 카드에 페인이 두개자나, 그냥 한개로 통합하ㅐ도 될거같아.
  user_added_at: 2026-05-10T17:46
- claude_ack: 2026-05-10T18:48
  done: false
  id: M12
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-10T18:48
  queued_at: 2026-05-10T18:29
  status: pending_confirmation
  text: 마일스톤 상태 (펜팅 / 큐 / 등등의 상태가 좀더 직관적으로 보이도록 수정해야함 - badge 상태를 텍스트로 표시하기바람)
  user_added_at: 2026-05-10T17:47
- claude_ack: 2026-05-10T18:03
  done: false
  id: M13
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-10T18:03
  status: pending
  text: terminal height longer * 1.5 and , width narrower to 3/5 to the current state,
  user_added_at: 2026-05-10T17:56
- claude_ack: 2026-05-10T18:49
  done: false
  id: M14
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-10T18:49
  queued_at: 2026-05-10T18:29
  status: pending_confirmation
  text: 대기중인 작업이 없다면 다음 큐를 바로 실행하도록해야한다. 그리고 유아이에서 등록된 마일스톤을 인지하는 시간을 줄이도록해야한다.
  user_added_at: 2026-05-10T18:24
- clarification_question: 이것은 구체적인 구현 요청인가요, 아니면 아키텍처 방향에 대한 질문인가요? 어떤 에이전트에게 위임하는
    방식을 원하시나요?
  claude_ack: '2026-05-10T18:29:24+09:00'
  done: false
  id: M15
  layer: 0
  parent_id: null
  status: needs_clarification
  text: 마일스톤 관리를 개별 에이전트에게 위임가능한가 (컨텍스트 문제는 어떡하나 ? )
  user_added_at: 2026-05-10T18:25
name: Claude-Hub
note: Personal AI MOAT — hub dashboard as the operational brain. Complete the hub
  first, then leverage it for content/career.
parent: null
position_x: 1
repo_path: /home/desk-1/.claude/hub
stage: unassigned
status: on-track
target: '100'
unit: '%'
x: 485
y: 0
---

# MOAT — North Star (redefined 2026-05-09)

## Why this metric
Hub dashboard is the operational center for all projects. Completing it to production quality
creates the foundation for everything else — content creation, career tracking, milestone management.
"Completeness %" = (passed invariants / 14) × 40 + milestone_done_ratio × 40 + mobile_score × 20.

## Current State (2026-05-09)
- E2E: 14/14 passing ✓
- Milestones: 3-state system working ✓
- Stop hook: 14-check verify integrated ✓
- Mobile: partial (text-size-adjust added today)
- Stable operation: hub host fixed to 0.0.0.0 ✓

## Strategy
1. Complete mobile UX (all panes + detail pane responsive on iPhone)
2. Stable ops (auto-restart, Tailscale file transfer)
3. Review all project NS stones for accuracy
4. Then pivot to content production using hub as the tracking system

## OKRs — 2026 Q2
- K1: Hub completeness score ≥ 90% by end of Q2
- K2: All 7 project NS stones non-rotted and current
- K3: iPhone → hub workflow working (file transfer + mobile access)

## Links
- Hub: http://100.119.82.4:9000
- Verify: python3 ~/.claude/hub/verify.py
- Source: ~/.claude/hub/