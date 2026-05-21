# Personal Hub Telemetry — Diagnostic Checklist

**Date**: 2026-05-14 **Corpus**: personal_hub_telemetry **Doc-ID**: D1
**Status**: auto-generated (Auto-Corpus Builder, `/entity -ccrd`)

---

## When to Use This Diagnostic

Run this checklist when:
- Designing a new telemetry schema for a self-hosted hub / dashboard
- Auditing an existing schema before shipping
- Reviewing whether a "telemetry" proposal is actually telemetry vs. logging vs. observability

Outputs:
- PASS / FAIL on 13 questions
- A *production-readiness verdict*: SHIP / SHIP WITH PATCHES / REWORK
- A *minimum-viable cut* if scope creep is detected

---

## 13-Question Audit

### Block A — Scope & Doctrine (Q1–Q3)

**Q1. Single-operator scope?**
- PASS: System has exactly one human operator (or ≤ 3 trusted collaborators on a single LAN/Tailscale net).
- FAIL: Multi-tenant, customer-facing, or shared-hosted. → Route to product-analytics literature.

**Q2. Retrospective query goal?**
- PASS: The operator wants to ask "what happened last week / month?" — not "alert me now."
- FAIL: Real-time SLO/alerting goal. → Route to observability stack.

**Q3. Opt-in default with visible indicator?**
- PASS: Telemetry OFF unless env var / config flag set; UI shows "telemetry ON" pill when active.
- FAIL: Hardcoded on, or no UI indicator. → HC-3 violation.

### Block B — Schema Discipline (Q4–Q7)

**Q4. ≤ 6 event types?**
- PASS: 4 base events + ≤ 2 optional. All map onto the 4-class taxonomy (lifecycle / state-transition / automation-dispatch / failure).
- FAIL: > 6 event types, or any event that doesn't fit a class. → HC-1 violation. Cut.

**Q5. All 4 slots filled per event?**
- PASS: Every event has WHEN (ts) + WHERE (proj_id, session_kind) + WHAT (event_name, payload) + HOW (action/mode/status).
- FAIL: Events missing slots are either too generic ("error happened") or too coupled to one feature ("button-foo clicked"). Refactor.

**Q6. Payload fields ≤ 6 per event?**
- PASS: Most events 3–5 fields. No event > 6 structured fields + 1 capped free-text.
- FAIL: Payload bloat. Each field is a future migration cost; audit which fields the operator will actually query.

**Q7. Free-text fields capped + path-stripped?**
- PASS: All free-text capped at 200 chars; regex strips `/home/<user>/...` paths and similar identifiers; no stack traces stored.
- FAIL: HC-4 violation. Content leak risk even at single-operator scale.

### Block C — Privacy & Storage (Q8–Q11)

**Q8. Zero PII fields?**
- PASS: No email, no IP, no user-agent, no API key, no transcript / milestone-body / commit-message content.
- FAIL: Strip the fields. Project IDs (user-chosen labels) are OK.

**Q9. Local-only storage, no auto-remote-sync?**
- PASS: SQLite file on local disk (or LAN-only volume). Export endpoint requires explicit operator action (manual `rsync`, `GET /export`).
- FAIL: Auto-syncs to VPS / S3 / cloud DB. → HC-6 violation.

**Q10. Storage engine matches volume?**
- PASS: < 50k events/day → SQLite. > 5M rows historical AND slow aggregate query observed → consider DuckDB migration.
- FAIL: DuckDB chosen pre-emptively (HC-2), OR JSONL-only with no structured query path.

**Q11. Retention policy documented and enforced?**
- PASS: 90-day rolling window (or operator-chosen explicit policy), with a cron / startup-hook that prunes.
- FAIL: No retention → DB grows unboundedly → operator eventually deletes the whole file out of frustration, losing all history.

### Block D — Operational Wiring (Q12–Q13)

**Q12. Error event whitelisted, not catch-all?**
- PASS: 3–6 named error categories (`spawn_fail`, `resume_stale`, `lock_stale`, `rate_limit`, `schema_validation_fail`). Other exceptions log to stderr only.
- FAIL: HC-5 violation. Unbounded `category` field will degrade to noise.

**Q13. Schema versioning in place?**
- PASS: `_schema_version` table or row exists; migrations are forward-only with documented version bumps.
- FAIL: First schema change will require manual DB surgery or a full drop+rebuild.

---

## Scoring

| PASS count | Verdict |
|---|---|
| 13 / 13 | **SHIP** — production-ready |
| 11–12 / 13 | **SHIP WITH PATCHES** — fix the 1–2 FAILs in the same iteration; do not block deadline |
| 8–10 / 13 | **REWORK** — substantive design gaps; resolve before ship |
| ≤ 7 / 13 | **STOP** — fundamental scope/doctrine errors; revisit T1 + T4 |

---

## Minimum Viable Cut (when deadline pressure forces it)

If the schema fails Q4 (too many event types) or Q6 (payload bloat) but the deadline is real, apply this cut in order:

1. **Drop optional events first**. `error_event` is optional in MVF. Lifecycle + state-transition + dispatch are the 3 mandatory base events.
2. **Drop derived/computable fields**. If `duration_sec` can be computed from paired attach/detach events, don't store it twice.
3. **Drop low-query-probability fields**. `wake_sent: bool` on `exec_dispatch` — does the operator's anticipated query care? If unclear, drop.
4. **Defer the export endpoint**. Operator can `sqlite3 telemetry.db` directly; web export is polish.
5. **Defer the UI pill**. A grep in the source file is enough until v2.

What MUST ship on day 1:
- `session_start` event
- `milestone_event` (or equivalent state-transition for the operator's main work primitive)
- `exec_dispatch` (or equivalent automation-dispatch event)
- Opt-in toggle (env var alone suffices; config file is polish)
- 90-day retention (a single `DELETE WHERE ts < ...` on boot is enough)

Everything else is iteration.

---

## Common Anti-Patterns Detected by This Diagnostic

- **"Just log every endpoint hit"** → Fails Q4 + Q6. The operator will never query 80% of these.
- **"Sync to my home server nightly"** → Fails Q9. Manual rsync is the correct primitive.
- **"Catch all exceptions to the DB"** → Fails Q12 + Q7 (stack traces leak code).
- **"Use Postgres because we might need it later"** → Pre-optimization for scale the system will never reach.
- **"Add a `tags: JSON` field for flexibility"** → Schema-less escape hatch that breaks Q6 discipline; everything ends up in `tags` and nothing is queryable.
- **"Track UI button clicks to optimize the interface"** → Single-operator UI doesn't need a/b testing data; the operator can just *say* the button is annoying.
