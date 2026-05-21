# Personal Hub Telemetry — Implementation Playbook

**Date**: 2026-05-14 **Corpus**: personal_hub_telemetry **Doc-ID**: S1
**Status**: auto-generated (Auto-Corpus Builder, `/entity -ccrd`)

---

## 3-Day Ship Plan (Minimum-Viable Telemetry)

Target: from zero to production-ready telemetry on a single-operator FastAPI hub, ≤ 3 working days, ≤ 150 LOC total.

### Day 1 — Schema + Writer (~80 LOC)

**Hour 1: schema file**
- Create `~/.claude/hub/telemetry_schema.sql` with 4 tables: `session_start`, `milestone_event`, `pty_attach` (or your hub's equivalent state-transition event), `exec_dispatch`.
- Each table: `id INTEGER PRIMARY KEY, ts TEXT NOT NULL, proj_id TEXT NOT NULL, ...` + event-specific fields.
- Add `_schema_version` table with single row `version INTEGER`.

**Hour 2: writer helper**
```
def _log_event(table: str, fields: dict) -> None:
    if not os.environ.get("HUB_TELEMETRY") == "1":
        return
    # opt-in gate first → zero-cost when disabled
    fields["ts"] = datetime.now(LOCAL_TZ).isoformat()
    # strip /home/<user>/ paths from any free-text field
    for k, v in fields.items():
        if isinstance(v, str) and "/home/" in v:
            fields[k] = re.sub(r"/home/[^/\s]+", "/home/USER", v)[:200]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(_build_insert(table, fields), tuple(fields.values()))
```

**Hour 3–4: wire 4 sites**
- Server boot → `_log_event("session_start", {...})`
- Milestone POST/PATCH/DELETE → `_log_event("milestone_event", {...})`
- WebSocket attach/detach handler → `_log_event("pty_attach", {...})`
- Execute endpoint / queue writer → `_log_event("exec_dispatch", {...})`

**Hour 5: smoke test**
- Boot server with `HUB_TELEMETRY=1`. Trigger one of each event. `sqlite3 telemetry.db 'SELECT * FROM ...'` returns rows.
- Boot server without env var. Trigger same events. DB unchanged.

**Day 1 exit criteria**: 4 events writing, opt-in gate verified, < 80 LOC delta.

### Day 2 — Hardening + Verification

**Hour 1: retention**
- On server boot, run `DELETE FROM <each_table> WHERE ts < datetime('now', '-90 days')`. ~5 LOC.

**Hour 2: UI indicator**
- When `HUB_TELEMETRY=1`, render a small `<span class="pill">telemetry ON</span>` in nav. Visible signal that the operator is being logged by their own tool.

**Hour 3–4: Docker verification**
- `Dockerfile` with `ENV HUB_TELEMETRY=1`, `VOLUME /data`, `EXPOSE 9000`.
- `docker build && docker run -v $(pwd)/data:/data ...`
- Hit one endpoint of each event class from host.
- Verify: `/data/telemetry.db` exists, each table has ≥ 1 row, no PII fields populated.
- `tcpdump -i any host <docker-bridge>` during a milestone create — confirm zero external network egress.

**Hour 5: privacy audit**
- Open the DB. `SELECT * FROM milestone_event LIMIT 50`. Eyeball for: emails, IPs, raw home paths, milestone titles in payload. If any present → tighten the strip regex.

**Day 2 exit criteria**: 90-day retention working, UI pill visible, Docker test green, privacy audit clean.

### Day 3 — Polish (optional, deadline-conditional)

**Hour 1–2: export endpoint**
- `GET /api/telemetry/export?format=csv` → stream CSV from each table.
- Auth: Tailscale-only IP check, or shared-secret header. No public exposure.

**Hour 3: dashboard view**
- Single page: counts per event class for last 7 / 30 / 90 days. Read-only.

**Hour 4: schema migration helper**
- A `migrate.py` that reads `_schema_version`, applies forward-only migrations from a `migrations/` dir.

**Day 3 exit criteria**: Export works, dashboard reads cleanly, migration path proven with a no-op v1→v2 bump.

### Cut Strategy if Deadline Slips

Drop in this order (each preserves the layer below):
1. Day 3 entirely → ship MVF
2. UI pill (Day 2 Hour 2) → defer; document the env var instead
3. Docker test (Day 2 Hour 3–4) → run a manual integration test instead
4. Retention (Day 2 Hour 1) → ship without; add as a cron later. Storage grows ~5 MB/month, tolerable for 6+ months.
5. `error_event` if it was in scope → drop entirely; this is the optional 5th event.

What CANNOT be cut:
- The 4 base events
- The opt-in gate
- The PII strip
- Schema versioning row (even if migrations come later)

---

## Schema Recipes

### Recipe A: NS Hub (concrete for `~/.claude/hub/`)

```sql
CREATE TABLE session_start (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    proj_id TEXT NOT NULL,
    session_kind TEXT NOT NULL,        -- 'hub' | 'pty' | 'exec'
    claude_resume_mode TEXT             -- 'fresh' | 'continue' | 'resume'
);

CREATE TABLE milestone_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    proj_id TEXT NOT NULL,
    mid TEXT NOT NULL,                  -- 'M161' etc.
    action TEXT NOT NULL,               -- 'create' | 'status_change' | 'comment_add' | 'reopen' | 'delete'
    from_status TEXT,
    to_status TEXT,
    author TEXT NOT NULL                -- 'user' | 'claude' | 'system'
);

CREATE TABLE pty_attach (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    proj_id TEXT NOT NULL,
    action TEXT NOT NULL,               -- 'attach' | 'detach' | 'kill'
    duration_sec INTEGER                -- only on detach/kill
);

CREATE TABLE exec_dispatch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    proj_id TEXT NOT NULL,
    mode TEXT NOT NULL,                 -- 'tmux_active' | 'tmux_new' | 'tmux_spawn_failed'
    queue_size INTEGER NOT NULL,
    wake_sent INTEGER NOT NULL          -- 0/1, SQLite bool
);

CREATE TABLE _schema_version (version INTEGER PRIMARY KEY);
INSERT INTO _schema_version VALUES (1);

-- Indexes (essential, cheap)
CREATE INDEX idx_ms_ts ON milestone_event(ts);
CREATE INDEX idx_ms_proj ON milestone_event(proj_id, ts);
CREATE INDEX idx_ed_ts ON exec_dispatch(ts);
```

### Recipe B: Generic single-operator dashboard (template)

Replace `milestone_event` and `pty_attach` with whatever the operator's primary work primitive and primary connection primitive are. The 4-slot discipline (WHEN / WHERE / WHAT / HOW) is universal; the table names are domain-specific.

---

## Operator-Side Queries (the ones that justify the schema)

Real questions the operator will ask in months 2–3 — verify the schema supports them before shipping.

```sql
-- "How many milestones did I close last week?"
SELECT proj_id, COUNT(*)
FROM milestone_event
WHERE action = 'status_change' AND to_status = 'done'
  AND ts > datetime('now', '-7 days')
GROUP BY proj_id;

-- "When was the last time exec_dispatch failed?"
SELECT ts, proj_id, queue_size
FROM exec_dispatch
WHERE mode = 'tmux_spawn_failed'
ORDER BY ts DESC LIMIT 5;

-- "How long are my pty sessions on average?"
SELECT proj_id, AVG(duration_sec) / 60.0 AS avg_minutes
FROM pty_attach
WHERE action IN ('detach', 'kill') AND duration_sec IS NOT NULL
GROUP BY proj_id;

-- "Days I was active on MOAT in the last 30 days"
SELECT DISTINCT date(ts)
FROM milestone_event
WHERE proj_id = 'MOAT' AND ts > datetime('now', '-30 days');
```

If any of these queries can't be answered with the schema → the schema has a gap. Fix before ship.

---

## Anti-Patterns Encountered in the Wild

| Anti-pattern | Symptom | Fix |
|---|---|---|
| "Telemetry as logging" | Free-text `message` field on every event | Replace with structured `action` + `status` enums |
| "Backup via auto-sync" | Cron job uploads DB to S3 nightly | Remove cron; manual `rsync` only |
| "Just one more event type" | 11 tables after 3 months | Audit query history; consolidate or drop the bottom-half-of-queries |
| "Capture stack traces for debugging" | `details` field contains 4KB of trace | Stderr only; never DB |
| "Use ORM for type safety" | SQLAlchemy + Alembic + 200 LOC of model classes | Raw SQL is fine at this scale; ORM is post-Day-3 polish at best |

---

## When to Graduate Beyond This Playbook

Trigger conditions:
- DB row count > 5M, AND aggregate queries > 1s → consider DuckDB migration
- More than 3 collaborators routinely use the hub → telemetry needs per-user identity + consent model; route to product-analytics literature
- Need real-time alerting (e.g. "wake me when exec_dispatch fails") → bolt a Prometheus exporter onto the same SQLite tables; do not abandon the schema

Until those triggers fire, the 3-day playbook above is the entire surface area.
