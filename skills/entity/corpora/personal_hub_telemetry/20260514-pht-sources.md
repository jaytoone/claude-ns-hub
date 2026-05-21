# Personal Hub Telemetry — Sources

**Date**: 2026-05-14 **Corpus**: personal_hub_telemetry **Doc-ID**: S1-sources
**Status**: auto-generated (Auto-Corpus Builder, `/entity -ccrd`)

---

## Primary Sources

### Telemetry doctrine (opt-in vs opt-out)
- [VSCode Telemetry Documentation](https://code.visualstudio.com/docs/configure/telemetry) — canonical opt-out reference with classification taxonomy.
- [GitHub microsoft/vscode#176269 — Require user consent before sending any telemetry](https://github.com/microsoft/vscode/issues/176269) — extended debate on GDPR Article 15 access rights vs. notification-only consent.
- [GitHub Microsoft/vscode#3182 — Telemetry opt-out](https://github.com/Microsoft/vscode/issues/3182) — origin issue tracking VSCode's opt-out implementation.
- [Make telemetry Data opt-in — Lightrun](https://lightrun.com/answers/microsoft-vscode-make-telemetry-data-opt-in) — community case for opt-in default.
- [The telemetry data content in Visual Studio Code — Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5741999/the-telemetry-data-content-in-visual-studio-code) — what fields are/aren't collected (no usernames, no email, no code scan).

### Storage engine (SQLite vs DuckDB vs JSONL)
- [DuckDB vs SQLite: A Complete Database Comparison — DataCamp](https://www.datacamp.com/blog/duckdb-vs-sqlite-complete-database-comparison) — row vs. column orientation tradeoffs.
- [DuckDB vs SQLite: The 2025 Data Analysis Showdown — Medium](https://medium.com/@bhagyarana80/duckdb-vs-sqlite-the-2025-data-analysis-showdown-0f01711db50b) — 10–100× column-scan speedup claim, with caveats for small-scale workloads.
- [Embedded Databases in 2026: DuckDB, SQLite, Polars, chDB — Kestra](https://kestra.io/blogs/embedded-databases) — selection matrix.
- [DuckDB vs SQLite: Performance, Speed, and Use Cases — Hakuna Matata Tech](https://www.hakunamatatatech.com/our-resources/blog/sqlite) — OLTP vs OLAP framing.
- [The SQLite Renaissance: Why the World's Most Deployed Database Is Taking Over Production in 2026 — DEV.to](https://dev.to/pockit_tools/the-sqlite-renaissance-why-the-worlds-most-deployed-database-is-taking-over-production-in-2026-3jcc) — Turso / Cloudflare D1 / LibSQL / Litestream context.
- [DuckDB for In-Repo Analytics — DEV.to](https://dev.to/pullflow/duckdb-for-in-repo-analytics-warehouse-grade-queries-in-your-pull-requests-4ha7) — crossover point where DuckDB wins.

### Self-hosted analytics (privacy-preserving)
- [Self-Hosted Web Analytics 2026: Plausible vs Matomo vs Umami vs OpenPanel — OpenPanel](https://openpanel.dev/articles/self-hosted-web-analytics) — feature/privacy comparison matrix.
- [8 best open source analytics tools you can self-host — PostHog](https://posthog.com/blog/best-open-source-analytics-tools) — Plausible, Umami, Matomo, GoatCounter, Fathom, Ackee, Shynet, PostHog itself.
- [Plausible — A Self-Hosted Privacy-Friendly Analytics Platform — Noted](https://noted.lol/plausible/) — opt-in deployment model.
- [Modern Self-Hosted Tools for Privacy and Control in 2026 — DEV.to](https://dev.to/lightningdev123/modern-self-hosted-tools-for-privacy-and-control-in-2026-1e6k) — broader category survey.
- [Self-Hosted Analytics: Docker & Privacy-First — Chris LaPointe](https://www.zdyn.net/docker/2021/07/02/simple-analytics.html) — Docker-based deployment pattern.

### FastAPI / Python event tracking
- [SQL (Relational) Databases — FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/) — canonical SQLite-with-FastAPI pattern.
- [FastAPI with SQL Databases | SQLite — GeeksforGeeks](https://www.geeksforgeeks.org/python/fastapi-sqlite-databases/) — minimal integration example.
- [CRUDAdmin — Modern admin interface for FastAPI with event tracking — GitHub](https://github.com/benavlabs/crudadmin) — reference for built-in event tracking pattern.

### Observability vs telemetry (boundary literature)
- [QCon London 2026: Wrangling Telemetry at Scale, a Guide to Self-Hosted Observability — InfoQ](https://www.infoq.com/news/2026/03/self-hosted-observability/) — distinguishes metrics-logs-traces (observability) from event telemetry; reinforces scope-gate.

---

## How These Sources Map to the Corpus

| Doc | Sources used | Key claim grounded |
|---|---|---|
| T1 (Theory) | VSCode docs, DuckDB/SQLite Medium, Kestra, OpenPanel, PostHog, SQLite Renaissance | Trilemma framing; storage engine selection; opt-in doctrine |
| T4 (Falsification) | VSCode opt-out criticism (GitHub issues), DuckDB crossover point | HC-2 (DuckDB premature), HC-3 (opt-in), HC-4 (PII vs content) |
| D1 (Diagnostic) | T1 + T4 internal cross-reference | 13-question audit derived from T4 hard constraints |
| S1 (Playbook) | FastAPI SQL tutorial, CRUDAdmin reference, Plausible/Umami deployment patterns | Day-1 to Day-3 implementation order |

---

## Sources NOT Used (and why)

- Big-tech observability literature (Google SRE Book, Honeycomb blog) — out of scope (multi-tenant, SLO-focused).
- GDPR primary text — referenced indirectly via VSCode debate; primary text not needed for single-operator scope.
- Postgres / TimescaleDB docs — single-operator scale doesn't justify; deferred to graduation triggers in S1.
- A/B testing / experiment design papers — N=1 single operator makes cohort comparison moot.

---

## Future Source Additions (when corpus matures)

- A live operator post-mortem after 90 days of use (would become V1 — empirical validation doc).
- A second case study from a different self-hosted hub (would extend the 4-class taxonomy beyond NS Hub specifics).
- A privacy incident retrospective if/when HC-4 is violated in practice.
