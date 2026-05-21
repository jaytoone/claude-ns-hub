# Personal Hub Telemetry — Theory

**Date**: 2026-05-14 **Corpus**: personal_hub_telemetry **Doc-ID**: T1
**Status**: auto-generated (Auto-Corpus Builder, `/entity -ccrd`) | **Sources**: VSCode telemetry docs, DuckDB/SQLite 2025-26 comparisons, Plausible/Umami/OpenPanel self-hosted analytics 2026, FastAPI event-tracking patterns

---

## Domain Definition

**Personal Hub Telemetry** = the event-logging layer for a *single-operator*, *self-hosted* productivity dashboard (e.g. `~/.claude/hub/` North Star hub on Tailscale at `http://100.119.82.4:9000`). The operator is also the data subject. There is no remote tenant, no aggregation, no shared multi-user analytics surface.

This is a deliberately *narrow* domain. It is NOT:
- Product analytics for an external user base (use `marketing_growth` + PostHog/Plausible patterns)
- B2B SaaS observability (use OpenTelemetry / metrics-logs-traces "3 pillars")
- Per-feature A/B testing infrastructure

It IS:
- Tracking which dashboard surfaces the operator actually uses
- Detecting failure modes in long-running automation (Stop hooks, exec queues, tmux respawns)
- Providing the operator a longitudinal view of their own workflow without leaking to third parties

---

## Core Theory

### The Personal Telemetry Trilemma

```
Usefulness × Privacy × Maintenance_Cost = constant
```

For a single-operator hub you cannot maximize all three. The minimum-viable design picks one to fix and trades the others:

| Anchor | Implication |
|---|---|
| **Fix Privacy at 100% local** | Usefulness capped at retrospective single-machine analytics; no cross-device aggregation |
| **Fix Usefulness (rich aggregates)** | Either accept maintenance cost of a real DB engine, or accept privacy cost of remote sync |
| **Fix Maintenance at near-zero** | Append-only JSONL only; you give up structured query power without a separate read path |

The dominant 2026 pattern for "I want personal observability of my own tools" is: **fix privacy, accept retrospective-only usefulness, minimize maintenance with SQLite + a 50-line writer.**

### Single-Operator Cost-of-Telemetry Formula

```
Telemetry_Cost = (Schema_Surface_Area × Event_Rate × Write_Hot_Path_Latency)
                  + Schema_Migration_Risk
                  + Privacy_Audit_Burden
Telemetry_Value = Pr(operator_will_query_it) × Decision_Impact_When_Queried
```

A single-operator system almost always has `Pr(operator_will_query_it) ≈ 0.1`. This is the dominant variable. Most personal telemetry projects fail at the query step, not the collection step.

**Implication**: collect minimally, but bias toward events the operator *will* want to grep 3 months from now during a post-mortem. Counts of UI-button clicks fail this test. Records of automation dispatches, queue states, and error categories pass it.

### The 4 Event Classes (single-operator hub)

1. **Lifecycle events** — server boot/shutdown, session attach/detach. *Tells you when the system was alive.*
2. **State-transition events** — milestone status changes, queue offset advances, lock acquisitions. *Tells you what the operator was doing through the system.*
3. **Automation-dispatch events** — exec queue writes, hook fires, cron triggers, tmux spawn results. *Tells you whether the automation kept up.*
4. **Failure events** — spawn fails, stale locks, rate-limit hits, schema-validation rejects. *Tells you why a past 'why didn't this run?' happened.*

Anything outside these 4 classes is **decoration** for a single-operator system.

### Storage Engine: SQLite vs DuckDB vs JSONL

| Engine | Best for | Cost |
|---|---|---|
| **JSONL (append-only)** | Lifecycle + dispatch streams. Crash-safe, grep-able. | No aggregation primitives; need separate reader. |
| **SQLite** | State transitions, structured queries, low-volume aggregates. ACID. | Schema migrations need discipline; column-scan slow at millions of rows. |
| **DuckDB** | Heavy analytical aggregates over months of events. 10–100× faster than SQLite on column scans. | Heavier dependency; overkill at personal-scale volumes. |

**For < 50k events/day (typical single-operator hub): SQLite wins.** The crossover where DuckDB beats SQLite for personal use is when row counts exceed ~5M and queries are aggregation-heavy. Single-operator hubs almost never hit this.

**Hybrid pattern (2026 default for self-hosted)**: JSONL for raw stream (durable append), nightly compact into SQLite for queryable history. Hub at single-operator scale rarely justifies the hybrid; pure SQLite is fine.

### Opt-In Default Doctrine

Industry-credibility precedent in 2025–2026:
- VSCode = opt-out (criticized for GDPR ambiguity; legally defensible but reputationally costly)
- Homebrew = opt-out with prominent toggle (similar criticism)
- Plausible / Umami / OpenPanel (self-hosted analytics) = opt-in by deployment choice
- HashiCorp tools (Terraform, Vault) = opt-out with one-flag disable

For a *personal* hub where the operator IS the data subject, the opt-in/opt-out distinction is partly moot — you cannot violate your own consent. The discipline matters anyway because:
1. The hub may later be shared with collaborators
2. It demonstrates the operator's own privacy ethics in code
3. Reversible defaults (opt-in) cost ~5 lines and prevent the system from becoming a hidden self-surveillance leak when copied/forked

**Doctrine**: default to **opt-in via env var or config file**, ship the flag enabled in the operator's own config, document the toggle. Cost = ~5 lines; benefit = "fork this safely" property.

---

## Framework: 4-Slot Schema for Single-Operator Hubs

```
Slot 1: WHEN  → ISO8601 timestamp + local timezone
Slot 2: WHERE → proj_id (label, not personal data) + session_kind
Slot 3: WHAT  → event_class + event_name + structured payload
Slot 4: HOW   → action / mode / status (the verb that fired the event)
```

Every event must fill all 4 slots. Missing slots are an anti-pattern signal — the event is either too generic ("an error happened") or too tightly coupled to one feature ("button-foo clicked").

### Payload Field Discipline

- **No PII**: no email, no IP, no user-agent strings, no API keys, no transcript content
- **No claim text**: milestone titles / commit messages / chat content are user IP; count events, never store contents
- **Project IDs allowed**: user-chosen labels like `MOAT`, `CTX` are not personal data
- **Free-text fields**: capped (≤200 chars), regex-strip `/home/<user>/...` paths, no stack traces

### Retention

90-day rolling window is the 2026 personal-scale norm. Pragma `optimize` + a cron `DELETE WHERE ts < now() - 90d` is sufficient. No backup, no remote sync; the operator can `rsync` manually if they want longer history.

---

## Scope Boundaries

This corpus applies when:
- The system has exactly **one human operator** (or a tightly bounded N ≤ 3 trusted collaborators)
- Data stays on the operator's machine or LAN/Tailscale (no third-party cloud analytics)
- The goal is *retrospective debugging + workflow self-awareness*, not product growth

This corpus does NOT apply when:
- External users / customers send events (route to `marketing_growth` or product analytics literature)
- The "telemetry" is actually metrics for an SLO/uptime dashboard (route to observability frameworks: OpenTelemetry, Prometheus)
- Decisions need cohort comparison or A/B testing (route to `marketing_growth` / `monetization`)

---

## Sources

- [VSCode Telemetry docs](https://code.visualstudio.com/docs/configure/telemetry)
- [GitHub microsoft/vscode#176269 — opt-in consent debate](https://github.com/microsoft/vscode/issues/176269)
- [DuckDB vs SQLite 2025 Showdown — Medium](https://medium.com/@bhagyarana80/duckdb-vs-sqlite-the-2025-data-analysis-showdown-0f01711db50b)
- [Embedded Databases in 2026 — Kestra](https://kestra.io/blogs/embedded-databases)
- [Self-Hosted Web Analytics 2026 — OpenPanel comparison](https://openpanel.dev/articles/self-hosted-web-analytics)
- [PostHog 8 best open-source analytics tools](https://posthog.com/blog/best-open-source-analytics-tools)
- [The SQLite Renaissance 2026 — DEV.to](https://dev.to/pockit_tools/the-sqlite-renaissance-why-the-worlds-most-deployed-database-is-taking-over-production-in-2026-3jcc)
- [FastAPI SQL Databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
