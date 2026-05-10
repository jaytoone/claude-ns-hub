---
name: CGR re-scoped as skill-level QG29
description: The CGR (Compute-Grounded Reasoning) artifact from arXiv:2604.12102 was designed against Python files that do not exist — re-scoped to a skill-level QG29 check in Entity SKILL.md. Use for any future CGR-related work.
type: project
originSessionId: 9d7d186b-227d-481d-a1b6-874de9a0cd8d
---
CGR artifact (`experiments/stuck_agent/cgr_compute_grounded_reasoning_design.md`) was exhaled against a hypothetical architecture that did not match reality. Reality check done 2026-04-17:

- `scripts/corpus_router.py` — does not exist
- `scripts/quality_gate.py` — does not exist
- QG26 (ACTION-UNCERTAIN) is row #26 in `~/.claude/skills/entity/SKILL.md` — a prompt-level check, not a Python classifier

**Why**: Entity's Quality Gate is skill-prompt-level (27 checks defined in the entity SKILL.md markdown table), not a Python module. The original plan confused "extend the Quality Gate" with "extend a Python module".

**How to apply**:
- Any CGR / grounding-extension work goes into `~/.claude/skills/entity/SKILL.md` as a new QG row + spec block (pattern: see QG29 spec after QG28 in the file).
- Tag format: `[CGR:tool:target]` (e.g., `[CGR:grep:QG26:entity/SKILL.md]`). Fabricated receipts FAIL QG29.
- Measurement harness: `experiments/hypothesis_validation/cgr_compliance_harness.py` invokes `claude -p` and scrapes tag density from responses.
- Skill count went 27 → 29 (QG28 = Convergent conclusion, QG29 = CGR compute grounding).
- If exhale proposes a future artifact that says "extend `scripts/X.py`" where X is a prompt-level concept, flag it as the same mistake pattern.
