// M1517: Cloudflare Worker — Hub telemetry relay
// Receives session_aggregate POSTs from hub clients, forwards to Turso (private).
// Deploy: wrangler deploy. Set secrets: TURSO_URL, TURSO_TOKEN, RELAY_SECRET (optional).
//
// Client side: POST <worker-url>/v1/session-aggregate with JSON body matching
// hub_session_aggregates schema. Optional header: X-Relay-Secret for abuse protection.

const TABLE_SCHEMA = `CREATE TABLE IF NOT EXISTS hub_session_aggregates (
  schema_version TEXT, install_id TEXT, ts_date TEXT, ts_uploaded INTEGER,
  hub_version TEXT, os TEXT, action_count INTEGER, tool_trace_count INTEGER,
  mean_tool_duration_ms REAL, stone_complete_count INTEGER, project_count INTEGER,
  tool_hist_json TEXT, outcome_hist_json TEXT, k_count INTEGER
)`;

const ALLOWED_FIELDS = new Set([
  "schema_version", "install_id", "ts_date", "ts_uploaded",
  "hub_version", "os", "action_count", "tool_trace_count",
  "mean_tool_duration_ms", "stone_complete_count", "project_count",
  "tool_hist_json", "outcome_hist_json", "k_count",
]);

const INT_FIELDS = new Set([
  "ts_uploaded", "action_count", "tool_trace_count",
  "stone_complete_count", "project_count", "k_count",
]);

const FLOAT_FIELDS = new Set(["mean_tool_duration_ms"]);

async function handleAggregate(request, env) {
  // Optional shared-secret check (set RELAY_SECRET via `wrangler secret put`)
  if (env.RELAY_SECRET) {
    const sent = request.headers.get("X-Relay-Secret") || "";
    if (sent !== env.RELAY_SECRET) {
      return new Response("forbidden", { status: 403 });
    }
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ ok: false, error: "invalid json" }), { status: 400 });
  }

  // Filter to allowed fields only (defense against schema injection)
  const filtered = {};
  for (const [k, v] of Object.entries(body)) {
    if (ALLOWED_FIELDS.has(k) && v != null) filtered[k] = v;
  }
  if (Object.keys(filtered).length === 0) {
    return new Response(JSON.stringify({ ok: false, error: "no valid fields" }), { status: 400 });
  }

  // Hard size limit — prevent abuse via huge tool_hist_json
  for (const k of ["tool_hist_json", "outcome_hist_json"]) {
    if (typeof filtered[k] === "string" && filtered[k].length > 8192) {
      filtered[k] = filtered[k].slice(0, 8192);
    }
  }

  const cols = Object.keys(filtered);
  const placeholders = cols.map(() => "?").join(", ");
  const args = cols.map((c) => {
    const v = filtered[c];
    if (INT_FIELDS.has(c)) return { type: "integer", value: String(parseInt(v, 10) || 0) };
    if (FLOAT_FIELDS.has(c)) return { type: "float", value: parseFloat(v) || 0 };
    return { type: "text", value: String(v) };
  });

  const payload = {
    requests: [
      { type: "execute", stmt: { sql: TABLE_SCHEMA } },
      {
        type: "execute",
        stmt: {
          sql: `INSERT INTO hub_session_aggregates (${cols.join(", ")}) VALUES (${placeholders})`,
          args,
        },
      },
    ],
  };

  try {
    const resp = await fetch(`${env.TURSO_URL}/v2/pipeline`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.TURSO_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const txt = await resp.text();
      return new Response(JSON.stringify({ ok: false, error: `turso ${resp.status}`, detail: txt.slice(0, 200) }), {
        status: 502,
      });
    }
    const result = await resp.json();
    const errs = (result.results || []).filter((r) => r.type === "error");
    if (errs.length) {
      return new Response(JSON.stringify({ ok: false, error: "turso_sql_error", detail: errs[0] }), { status: 502 });
    }
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e).slice(0, 200) }), { status: 502 });
  }
}

// M1517: hub_usage event relay — single-row INSERT into hub_usage table.
async function handleHubUsage(request, env) {
  if (env.RELAY_SECRET) {
    const sent = request.headers.get("X-Relay-Secret") || "";
    if (sent !== env.RELAY_SECRET) return new Response("forbidden", { status: 403 });
  }
  let body;
  try { body = await request.json(); }
  catch { return new Response(JSON.stringify({ ok: false, error: "invalid json" }), { status: 400 }); }
  const ts = parseInt(body.ts, 10) || 0;
  const event = String(body.event || "").slice(0, 100);
  const install_id = String(body.install_id || "").slice(0, 32);
  const version = String(body.version || "").slice(0, 32);
  const os = String(body.os || "").slice(0, 32);
  const extra_json = String(body.extra_json || "").slice(0, 4096);
  if (!event || !install_id) return new Response(JSON.stringify({ ok: false, error: "missing event/install_id" }), { status: 400 });
  const payload = {
    requests: [
      { type: "execute", stmt: { sql: "CREATE TABLE IF NOT EXISTS hub_usage (ts INTEGER, event TEXT, install_id TEXT, version TEXT, os TEXT, extra_json TEXT)" } },
      { type: "execute", stmt: {
        sql: "INSERT INTO hub_usage (ts, event, install_id, version, os, extra_json) VALUES (?, ?, ?, ?, ?, ?)",
        args: [
          { type: "integer", value: String(ts) },
          { type: "text", value: event }, { type: "text", value: install_id },
          { type: "text", value: version }, { type: "text", value: os },
          { type: "text", value: extra_json },
        ],
      } },
    ],
  };
  try {
    const resp = await fetch(`${env.TURSO_URL}/v2/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.TURSO_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const txt = await resp.text();
      return new Response(JSON.stringify({ ok: false, error: `turso ${resp.status}`, detail: txt.slice(0, 200) }), { status: 502 });
    }
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e).slice(0, 200) }), { status: 502 });
  }
}

// M1517-test: admin-only read endpoint for verifying telemetry flow end-to-end.
// Requires X-Relay-Secret header. Returns row counts per table grouped by install_id.
async function handleAdminCount(request, env) {
  if (env.RELAY_SECRET) {
    const sent = request.headers.get("X-Relay-Secret") || "";
    if (sent !== env.RELAY_SECRET) return new Response("forbidden", { status: 403 });
  }
  try {
    const payload = {
      requests: [
        { type: "execute", stmt: { sql: "SELECT install_id, COUNT(*) AS n FROM hub_usage GROUP BY install_id ORDER BY n DESC LIMIT 50" } },
        { type: "execute", stmt: { sql: "SELECT install_id, COUNT(*) AS n FROM hub_session_aggregates GROUP BY install_id ORDER BY n DESC LIMIT 50" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_usage" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_session_aggregates" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_tool_trace" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_action_log" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_milestone_causal" } },
        { type: "execute", stmt: { sql: "SELECT COUNT(*) AS total FROM hub_stone_text" } },
      ],
    };
    const resp = await fetch(`${env.TURSO_URL}/v2/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.TURSO_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    return new Response(JSON.stringify(data), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e).slice(0, 200) }), { status: 502 });
  }
}

// M1516-ext: generic batch INSERT helper — shared by tool_trace, action_log, milestone_causal.
async function handleBatchInsert(request, env, tableName, createSql, allowedCols, intCols, floatCols, truncCols) {
  if (env.RELAY_SECRET) {
    const sent = request.headers.get("X-Relay-Secret") || "";
    if (sent !== env.RELAY_SECRET) return new Response("forbidden", { status: 403 });
  }
  let body;
  try { body = await request.json(); }
  catch { return new Response(JSON.stringify({ ok: false, error: "invalid json" }), { status: 400 }); }

  const installId = String(body.install_id || "").slice(0, 32);
  const rows = Array.isArray(body.rows) ? body.rows : [];
  if (!installId || rows.length === 0) {
    return new Response(JSON.stringify({ ok: false, error: "missing install_id or rows" }), { status: 400 });
  }

  const requests = [{ type: "execute", stmt: { sql: createSql } }];
  for (const row of rows.slice(0, 500)) {
    const cols = ["install_id"];
    const args = [{ type: "text", value: installId }];
    for (const col of allowedCols) {
      if (row[col] == null) continue;
      cols.push(col);
      let v = row[col];
      if (truncCols && truncCols[col]) v = String(v).slice(0, truncCols[col]);
      if (intCols && intCols.has(col)) args.push({ type: "integer", value: String(parseInt(v, 10) || 0) });
      else if (floatCols && floatCols.has(col)) args.push({ type: "float", value: parseFloat(v) || 0 });
      else args.push({ type: "text", value: String(v) });
    }
    const placeholders = cols.map(() => "?").join(", ");
    requests.push({ type: "execute", stmt: {
      sql: `INSERT INTO ${tableName} (${cols.join(", ")}) VALUES (${placeholders})`, args
    }});
  }

  try {
    const resp = await fetch(`${env.TURSO_URL}/v2/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.TURSO_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ requests }),
    });
    if (!resp.ok) {
      const txt = await resp.text();
      return new Response(JSON.stringify({ ok: false, error: `turso ${resp.status}`, detail: txt.slice(0, 200) }), { status: 502 });
    }
    const result = await resp.json();
    const errs = (result.results || []).filter((r) => r.type === "error");
    if (errs.length) return new Response(JSON.stringify({ ok: false, error: "turso_sql_error", detail: errs[0] }), { status: 502 });
    return new Response(JSON.stringify({ ok: true, inserted: rows.length }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e).slice(0, 200) }), { status: 502 });
  }
}

// M1516-ext: POST /v1/tool-trace-batch
function handleToolTraceBatch(request, env) {
  return handleBatchInsert(request, env,
    "hub_tool_trace",
    `CREATE TABLE IF NOT EXISTS hub_tool_trace (
      install_id TEXT, id INTEGER, ts TEXT, proj_id TEXT, stone_id TEXT,
      session_id TEXT, tool_name TEXT, input_summary TEXT, output_summary TEXT, duration_ms INTEGER
    )`,
    ["id", "ts", "proj_id", "stone_id", "session_id", "tool_name", "input_summary", "output_summary", "duration_ms"],
    new Set(["id", "duration_ms"]),
    null,
    { input_summary: 200, output_summary: 200, tool_name: 64, proj_id: 64, stone_id: 64, session_id: 64 }
  );
}

// M1516-ext: POST /v1/action-log-batch
function handleActionLogBatch(request, env) {
  return handleBatchInsert(request, env,
    "hub_action_log",
    `CREATE TABLE IF NOT EXISTS hub_action_log (
      install_id TEXT, id INTEGER, ts TEXT, proj_id TEXT, stone_id TEXT,
      action TEXT, detail TEXT, session_id TEXT
    )`,
    ["id", "ts", "proj_id", "stone_id", "action", "detail", "session_id"],
    new Set(["id"]),
    null,
    { action: 100, detail: 200, proj_id: 64, stone_id: 64, session_id: 64 }
  );
}

// M775/M1516-ext: POST /v1/milestone-causal-batch
function handleMilestoneCausalBatch(request, env) {
  return handleBatchInsert(request, env,
    "hub_milestone_causal",
    `CREATE TABLE IF NOT EXISTS hub_milestone_causal (
      install_id TEXT, rowid INTEGER, stone_id TEXT, proj_id TEXT,
      outcome_label TEXT, counterfactual_pair_id TEXT,
      goal_tree_snapshot TEXT, prompt_provenance TEXT, confounder TEXT, done_at TEXT
    )`,
    ["rowid", "stone_id", "proj_id", "outcome_label", "counterfactual_pair_id",
     "goal_tree_snapshot", "prompt_provenance", "confounder", "done_at"],
    new Set(["rowid"]),
    null,
    { outcome_label: 64, counterfactual_pair_id: 64, goal_tree_snapshot: 2000,
      prompt_provenance: 500, confounder: 500, stone_id: 64, proj_id: 64 }
  );
}

// M1516-text: POST /v1/stone-text-batch
function handleStoneTextBatch(request, env) {
  return handleBatchInsert(request, env,
    "hub_stone_text",
    `CREATE TABLE IF NOT EXISTS hub_stone_text (
      install_id TEXT, rowid INTEGER, stone_id TEXT, proj_id TEXT,
      text TEXT, status TEXT, done_at TEXT, model_used TEXT
    )`,
    ["rowid", "stone_id", "proj_id", "text", "status", "done_at", "model_used"],
    new Set(["rowid"]),
    null,
    { stone_id: 64, proj_id: 64, status: 32, model_used: 64 }
  );
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/v1/session-aggregate" && request.method === "POST") {
      return handleAggregate(request, env);
    }
    if (url.pathname === "/v1/hub-usage" && request.method === "POST") {
      return handleHubUsage(request, env);
    }
    if (url.pathname === "/v1/tool-trace-batch" && request.method === "POST") {
      return handleToolTraceBatch(request, env);
    }
    if (url.pathname === "/v1/action-log-batch" && request.method === "POST") {
      return handleActionLogBatch(request, env);
    }
    if (url.pathname === "/v1/milestone-causal-batch" && request.method === "POST") {
      return handleMilestoneCausalBatch(request, env);
    }
    if (url.pathname === "/v1/stone-text-batch" && request.method === "POST") {
      return handleStoneTextBatch(request, env);
    }
    if (url.pathname === "/v1/admin/count" && request.method === "GET") {
      return handleAdminCount(request, env);
    }
    if (url.pathname === "/health" && request.method === "GET") {
      return new Response(JSON.stringify({ ok: true, service: "hub-telemetry-relay" }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response("not found", { status: 404 });
  },
};
