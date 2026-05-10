---
name: ameva to entity skill rename
description: All ameva-related skill names renamed to entity (ameva → entity, ameva-live → entity-live, ameva-inf → entity-inf)
type: project
---

All ameva skill names renamed to entity on 2026-04-16.

**Why:** User decision to unify naming under "entity" brand. ameva was built on entity base + corpus router.

**How to apply:**
- `/entity` = corpus-routed vertical AI scaffold (was `/ameva`)
- `/entity-live` = standalone bounded swarm loop (was `/ameva-live`)
- `/entity-inf` = standalone infinite corpus evolution loop (was `/ameva-inf`)
- Old `/entity` (base reasoning pipeline) content backed up as `SKILL.md.entity-backup`
- Old ameva directories preserved until confirmed safe to delete
- References updated in: live, live-inf, evolve, conceptual skills
- State directory: `.entity/` (was `.ameva/`)
- Metrics tag: `[ENTITY_GROUNDING_METRICS]` (was `[AMEVA_GROUNDING_METRICS]`)
- Signal detection variable: `is_entity_corpus` (was `is_ameva_corpus`)
