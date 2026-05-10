# Entity Project Memory

- [project_stuck_agent_state.md](project_stuck_agent_state.md) — Stuck-Agent 실험 보류 시점 상태 (2026-03-31)
- [concept_entity_definition.md](concept_entity_definition.md) — entity = 지성체 재정의 (Conceptual 기준, 자율 에이전트 아님)
- [entity-live/entity-inf rewrite](ameva-loop-rewrite.md) — thin wrapper → standalone swarm loop (2026-04-15)
- [ameva → entity rename](ameva-to-entity-rename.md) — all ameva skill names renamed to entity (2026-04-16)
- [conclusion readability](feedback_conclusion_readability.md) — CONCLUSION은 세줄결론(판단/근거/조건)으로 시작 (2026-04-16)
- [live-state archive 2026-04-16](project_live_state_archive.md) — ameva 시대 live-state/goal-tree 아카이브, /live는 반드시 goal 인자 필요
- [live-inf autonomy](feedback_live_inf_autonomy.md) — /live-inf는 iter 사이 사용자 지시 대기 금지, 자율 continue가 기본, stop은 사용자 명시 중단만
- [context efficiency](feedback_context_efficiency.md) — 필요한 만큼만 서술, 장황한 커밋/리포트/반복 설명 금지
- [CGR→QG29 re-scope](project_cgr_qg29.md) — CGR artifact referenced scripts/corpus_router.py + scripts/quality_gate.py that do not exist. Re-scoped as skill-level QG29 in ~/.claude/skills/entity/SKILL.md. Entity QG is prompt-level, not Python. (2026-04-17)
- [episodes.jsonl sampling bias](project_episodes_sample_bias.md) — .omc/episodes.jsonl records success summaries, not per-iteration failures. Cannot test Mirage taxonomy H1 from this alone. Need per-iteration failure logging. (2026-04-17)
- [CGR parser trigger over-count](project_cgr_parser_fix.md) — CGR harness trigger regex counts each file-path mention as a separate claim; one [CGR:] tag can legitimately cover multiple mentions. Fix: group by claim identity before dividing tags/triggers. (2026-04-17)
- [Entity win/lose frame](project_entity_winloss_frame.md) — Entity thinks in win/lose (승패), not success/fail. Grounded in view that human world (politics/business/relations) is game-like. (2026-04-17)
