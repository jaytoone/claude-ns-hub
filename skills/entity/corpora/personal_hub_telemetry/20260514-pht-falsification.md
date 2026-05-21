# Personal Hub Telemetry — Falsification Criteria

**Date**: 2026-05-14 **Corpus**: personal_hub_telemetry **Doc-ID**: T4
**Status**: auto-generated (Auto-Corpus Builder, `/entity -ccrd`)

---

## Hard Constraints (HC) — Sycophancy Guard

### HC-1: "Just collect everything, query later"
**Violation signal**: Schema design with > 8 event types or > 6 payload fields per event on day 1.
**Why it fails**: Single-operator probability of querying any given event class ≈ 0.1. Each schema field is a future migration cost. Volume that never gets queried = pure cost.
**Correct response**: 4 base events + 1 optional. Add events only after the operator articulates a question SQLite can't already answer from existing data.

### HC-2: "DuckDB is faster, so use DuckDB"
**Violation signal**: Recommending DuckDB for a hub expected to log < 50k events/day.
**Why it fails**: DuckDB's column-scan advantage materializes at multi-million-row aggregates. At single-operator scale, SQLite's row-oriented writes and trivial migration story dominate. DuckDB is overkill until row count > ~5M *and* dominant queries are aggregations.
**Correct response**: SQLite default. Document the migration trigger (≥ 5M rows + slow aggregate query observed) but do not pre-optimize.

### HC-3: "Opt-out is fine because it's just me"
**Violation signal**: Hardcoding telemetry-on with no toggle, on grounds that the operator is the data subject.
**Why it fails**: Personal hubs get forked, shared, and gifted. An opt-out default propagates the operator's privacy stance to others without their consent. Also: opt-in costs ~5 lines; the marginal effort is near zero.
**Correct response**: env var or config-file toggle, default OFF in shipped code; operator enables in their own config. Visible UI indicator when active.

### HC-4: "Privacy = no PII, that's it"
**Violation signal**: Calling a telemetry schema "privacy-preserving" because it omits name/email/IP, while logging full file paths, commit hashes, milestone bodies, or chat content.
**Why it fails**: For a single operator, *content* is the high-leverage leak vector, not classical PII. Milestone text, file paths, and stack traces re-identify the operator's project trivially and leak intellectual property if the DB is ever shared.
**Correct response**: Strip `/home/<user>/...` paths via regex; cap free-text at 200 chars; never store milestone bodies, prompts, or transcript content. Count events, never store contents.

### HC-5: "Add an `error_event` for every exception"
**Violation signal**: Wiring `error_event` to a global `try/except` handler that catches everything.
**Why it fails**: Unbounded error categories explode the schema. The category field becomes useless ("misc: 8423") and stack traces leak code structure.
**Correct response**: Whitelist 3–6 error categories the operator will actually act on (`spawn_fail`, `resume_stale`, `lock_stale`, `rate_limit`, `schema_validation_fail`). Other exceptions log to stderr only.

### HC-6: "Remote sync is fine if it's just to my own server"
**Violation signal**: Recommending automatic sync to a VPS / S3 / cloud DB for "backup".
**Why it fails**: Network egress is the dominant privacy risk for a personal hub. Even "your own" remote server introduces (a) credential leak vectors, (b) shared-tenant compliance burden if the server hosts anything else, (c) silent failure modes where the operator forgets the sync is happening. Manual `rsync` is the correct primitive — it forces a conscious copy event.
**Correct response**: No automatic remote sync. Export endpoint + manual `rsync` if longer history desired. Document that the operator OWNS the sync decision.

### HC-7: "Ship the dashboard first, add telemetry later"
**Violation signal**: Treating telemetry as a v2 polish layer.
**Why it fails**: Retrofitting events into 50+ code sites is far costlier than wiring 4 events at first commit. Worse: by v2 you've forgotten the failure modes that prompted telemetry in the first place. The operator's "what went wrong yesterday?" question is already valuable on day 1.
**Correct response**: Day-1 telemetry, 4 events, ~80 LOC. The marginal cost is small enough that "skip it" is a false economy.

---

## Scope Gate Violations

This framework does NOT apply when:

1. **External user base sends events** → use product analytics (PostHog, Plausible, Umami) and `marketing_growth` corpus principles. Single-operator privacy doctrine is wrong frame.
2. **SLO / uptime monitoring is the goal** → use observability stack (Prometheus + Grafana + OpenTelemetry). Telemetry events are the wrong primitive; metrics + traces are.
3. **A/B testing or cohort analysis** → requires an external user base; single-operator data has N=1.
4. **Compliance audit telemetry (SOC2, HIPAA)** → requires immutable audit logs, signed events, retention policies far longer than 90 days. Different doctrine.
5. **Real-time alerting** → use a metrics pipeline (Prometheus → Alertmanager), not an event log. Personal telemetry is *retrospective by design*.

When scope is violated, route to the appropriate framework (`marketing_growth`, generic observability literature, or compliance frameworks) instead of forcing single-operator design on a multi-tenant problem.

---

## Falsification Conditions

The personal hub telemetry framework prediction **fails** if any of the following are observed:

- Operator queries the DB ≥ 3 times in 30 days but **none of the queries** map onto the 4 event classes (lifecycle / state-transition / automation-dispatch / failure). → The 4-class model is wrong for this operator's workflow; revisit class taxonomy.
- Storage cost grows > 100 MB/month at single-operator scale. → Payload discipline broken; audit field sizes and free-text caps.
- SQLite query latency > 1s for the operator's most common 90-day aggregate. → Row count likely > 5M (the DuckDB crossover); investigate before assuming the framework is wrong.
- Operator disables telemetry because the UI indicator is annoying or the data is "creepy." → Either the UI is too prominent (HC-3 over-correction) or the field discipline (HC-4) is leaking content. Diagnose before declaring the opt-in doctrine broken.
- A privacy incident occurs (DB shared, PII leaked) despite following HC-4. → Field discipline insufficient; tighten regex strip + drop free-text entirely.

If none of the above happens within 90 days of deployment, the framework is operating within design assumptions.

---

## Boundary with Adjacent Domains

| Adjacent domain | Where the boundary is |
|---|---|
| Product analytics (PostHog, Plausible) | External user base, K > 1 operators. Use cohort/funnel primitives. |
| Observability (OpenTelemetry, Prometheus) | SLO / latency / uptime goal. Use metrics + traces, not events. |
| Compliance audit logging | Immutable + signed + ≥ 7-year retention. Different primitives. |
| Application logs (stderr / loguru) | Human-readable real-time debug. Telemetry is structured + queryable + retrospective. |

The personal hub telemetry corpus is the *narrowest* of these four. When in doubt, ask: "Is the operator also the data subject? Is the query retrospective? Is the deployment single-machine?" If all three = YES, this corpus applies.
