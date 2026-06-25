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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/v1/session-aggregate" && request.method === "POST") {
      return handleAggregate(request, env);
    }
    if (url.pathname === "/v1/hub-usage" && request.method === "POST") {
      return handleHubUsage(request, env);
    }
    if (url.pathname === "/health" && request.method === "GET") {
      return new Response(JSON.stringify({ ok: true, service: "hub-telemetry-relay" }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response("not found", { status: 404 });
  },
};
