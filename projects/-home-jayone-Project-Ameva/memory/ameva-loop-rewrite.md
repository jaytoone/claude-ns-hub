---
name: ameva-live/ameva-inf standalone rewrite
description: ameva-live and ameva-inf rewritten from thin /live wrappers to standalone swarm loops with 4D Corpus Quality Oracle
type: project
---

ameva-live and ameva-inf were thin wrappers: /ameva → /live (or /live-inf). This caused knowledge task_type to DELEGATE back to ameva, skipping Wave 2 dev cycle, auto-oracle, and research agents entirely.

**Why:** /live's ORCHESTRATOR_MAP routes knowledge → ameva DELEGATE → autopilot skipped → scoring/evolution loop degrades to simple ameva repeat.

**How to apply:** Both skills now have standalone Explorer→Reasoner→Auditor swarm cycles with 4D Corpus Quality Oracle (grounding_rate, routing_precision, claim_quality, sycophancy_pass). State in `.ameva/` not `.omc/`. No omc-* dependencies. Based on spec: `docs/research/20260414-ameva-loop-skill-spec.md`.

Status: Iter 1 complete (2026-04-15). Auditor review pending (rate limit hit).
