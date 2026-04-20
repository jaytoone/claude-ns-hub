// CTX Dashboard client — connects to /stream SSE and renders snapshots.
// All telemetry-sourced strings are escaped before insertion to prevent XSS
// (defense in depth — the telemetry source is trusted local hooks, but
// hooks may log user prompts in future extensions).
const $ = (id) => document.getElementById(id);

const ESC_MAP = {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
function esc(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ESC_MAP[c]);
}

let activityPlot = null;
let graphNetwork = null;
let graphNodesSet = null;
let graphNodeById = {};
let lastEventCount = 0;   // used to detect new-event arrivals → refresh graph

function fmtThresholds(th) {
  return `Thresholds: CM ≥${th.cm_hybrid_min}%  |  g2_docs <${th.g2_docs_max}%  |  g2_grep <${th.g2_grep_max}%  |  p95 <${th.p95_max_ms}ms`;
}

function renderHealthRow(r) {
  const color = r.ok ? "green" : "yellow";
  const sym = r.ok ? "✓" : "~";
  const pct = Math.min(100, Math.max(2, Math.round((r.value || 0) * 100)));
  return `
    <div class="row">
      <div class="label">${esc(r.name)}</div>
      <div class="bar"><div class="bar-fill ${color}" style="width:${pct}%"></div></div>
      <div class="value">${esc(r.value_str)}</div>
      <div class="sym ${color}">${sym}</div>
      <div class="msg">${esc(r.msg)}</div>
    </div>`;
}

function renderLatencyBars(hist) {
  const total = hist.reduce((s, b) => s + b.count, 0) || 1;
  return hist.map(b => {
    const pct = (b.count / total) * 100;
    const danger = b.bucket === ">1s" || b.bucket === "500ms-1s";
    const fillColor = danger ? "red" : (b.bucket === "200-500ms" ? "yellow" : "green");
    return `
      <div class="b">
        <div class="bucket">${esc(b.bucket)}</div>
        <div class="bar"><div class="bar-fill ${fillColor}" style="width:${pct}%"></div></div>
        <div class="count">${esc(b.count)}</div>
      </div>`;
  }).join("");
}

function renderUtility(u) {
  const host = $("utility-body");
  if (!u || u.n_turns === 0) {
    host.innerHTML = `<div class="empty">
      No measurements yet. Complete a turn — CTX will log whether the
      assistant actually referenced injected context.
    </div>`;
    return;
  }
  const overall = u.overall_rate;
  const pct = overall == null ? 0 : Math.round(overall * 100);
  const cls = pct >= 50 ? "" : (pct >= 25 ? "mid" : "low");
  const blocks = u.by_block || {};
  const blockRows = Object.keys(blocks).sort().map(name => {
    const b = blocks[name];
    const p = Math.round((b.rate || 0) * 100);
    const color = p >= 50 ? "green" : (p >= 25 ? "yellow" : "red");
    const pctFill = Math.max(3, p);
    return `<div class="row">
      <div class="name">${esc(name)}</div>
      <div class="bar"><div class="bar-fill ${color}" style="width:${pctFill}%"></div></div>
      <div class="count">${p}% (${esc(b.referenced)}/${esc(b.total)})</div>
    </div>`;
  }).join("");
  host.innerHTML = `
    <div class="overall">
      <div class="big ${cls}">${pct}%</div>
      <div>
        <div>Overall utility</div>
        <div class="sub">${esc(u.n_turns)} turns measured · ${esc(u.total_items)} items injected</div>
      </div>
    </div>
    ${blockRows}
  `;
}

function renderNotices(notices) {
  if (!notices || notices.length === 0) {
    return `<div style="color:var(--text-dim); font-family:var(--mono); font-size:12px;">— none —</div>`;
  }
  return notices.map(n => `
    <div class="notice">
      <div class="tilde">~</div>
      <div class="metric">${esc(n.metric)}</div>
      <div class="msg">${esc(n.msg)}</div>
    </div>`).join("");
}

function renderOther(other) {
  if (!other || other.length === 0) return `<span style="color:var(--text-dim); font-size:11px;">— none —</span>`;
  return other.map(o => `<span class="pill">${esc(o.label)} <span class="count">×${esc(o.count)}</span></span>`).join("");
}

function fmtTs(ts) {
  if (!ts) return "";
  // ts is ISO8601 (from vault.db) — take HH:MM
  try {
    const s = String(ts);
    const m = s.match(/T(\d\d:\d\d)/);
    return m ? m[1] : s.slice(0, 16);
  } catch { return String(ts).slice(0, 16); }
}

function renderBlock(name, tag, items, itemClass = "it") {
  const cls = items && items.length ? "" : "empty";
  const body = items && items.length
    ? items.map(i => `<div class="${itemClass}" title="${esc(i)}">${esc(i)}</div>`).join("")
    : `<div class="it">— none —</div>`;
  return `
    <div class="block ${cls} ${name.toLowerCase()}">
      <div class="name"><span>${esc(name)}</span><span class="tag">${esc(tag)}</span></div>
      <div class="items">${body}</div>
    </div>`;
}

function renderCmBlock(cm) {
  const cls = cm && cm.length ? "" : "empty";
  const body = cm && cm.length
    ? cm.map(e => `
        <div class="cm-entry">
          <span class="who">${esc(e.role)}@${esc(e.project)}</span><span title="${esc(e.preview)}">${esc(e.preview)}</span>
        </div>`).join("")
    : `<div class="it">— none —</div>`;
  return `
    <div class="block cm ${cls}">
      <div class="name"><span>CM</span><span class="tag">chat memory</span></div>
      <div class="items">${body}</div>
    </div>`;
}

function renderGraphLegend() {
  const host = $("graph-legend");
  if (host.childElementCount > 0) return;  // render once
  host.innerHTML = `
    <span class="lg current"><span class="swatch"></span>current prompt</span>
    <span class="lg decision"><span class="swatch"></span>decision</span>
    <span class="lg doc"><span class="swatch"></span>doc</span>
    <span class="lg prompt"><span class="swatch"></span>past prompt</span>
    <span class="lg recall"><span class="line"></span>retrieval</span>
    <span class="lg topic"><span class="line"></span>topic (doc↔doc)</span>
    <span class="lg temporal"><span class="line"></span>temporal (decision↔decision)</span>
  `;
}

function nodeStyle(type) {
  // Larger minimums so hover hitboxes are mouse-friendly. Keeps hierarchy
  // (current > decision > doc > prompt) while making even the smallest
  // node comfortably clickable.
  switch (type) {
    case "current":  return {
      color: { background: "#3fb950", border: "#56d364", highlight: { background: "#56d364", border: "#7ee08f" }, hover: { background: "#56d364", border: "#7ee08f" } },
      size: 26, font: { color: "#fff", size: 14, face: "ui-monospace" }, shape: "dot", borderWidth: 3,
    };
    case "decision": return {
      color: { background: "#58a6ff", border: "#1f6feb", highlight: { background: "#79c0ff", border: "#388bfd" }, hover: { background: "#79c0ff", border: "#388bfd" } },
      size: 13, font: { color: "#c9d1d9", size: 11 }, shape: "dot", borderWidth: 1.5,
    };
    case "doc":      return {
      color: { background: "#bc8cff", border: "#8957e5", highlight: { background: "#d2a8ff", border: "#a371f7" }, hover: { background: "#d2a8ff", border: "#a371f7" } },
      size: 12, font: { color: "#c9d1d9", size: 11 }, shape: "dot", borderWidth: 1.5,
    };
    case "prompt":   return {
      color: { background: "#6e7681", border: "#8b949e", highlight: { background: "#8b949e", border: "#b1bac4" }, hover: { background: "#8b949e", border: "#b1bac4" } },
      size: 10, font: { color: "#8b949e", size: 10 }, shape: "dot", borderWidth: 1.5,
    };
    default: return { color: { background: "#888", border: "#666" }, size: 10, shape: "dot" };
  }
}

function edgeStyle(type, weight, isCurrent) {
  const base = {
    width: Math.max(0.6, Math.min(3.2, weight * 0.8)),
    smooth: { enabled: true, type: "continuous" },
  };
  // Retrieval edges (prompt → decision/doc) are the MAIN value signal — keep them vivid.
  // current = glowing green; past = saturated cyan (not faded dashed grey).
  if (type === "recall-d" || type === "recall-w") {
    const isDoc = type === "recall-w";
    return Object.assign(base, {
      color: isCurrent
        ? { color: "#3fb950", highlight: "#56d364", opacity: 1.0 }
        : { color: isDoc ? "#bc8cff" : "#58a6ff", highlight: "#3fb950", opacity: 0.85 },
      width: isCurrent ? Math.max(2.4, weight * 0.6) : Math.max(1.0, weight * 0.4),
      shadow: isCurrent ? { enabled: true, color: "#3fb950", size: 8, x: 0, y: 0 } : false,
    });
  }
  // Topic edges (doc ↔ doc) — cluster indicator, bright-ish purple
  if (type === "topic") {
    return Object.assign(base, {
      color: { color: "#bc8cff", highlight: "#d2a8ff", opacity: 0.55 },
      width: Math.max(0.8, weight * 3.0),
    });
  }
  // Temporal edges (same-day decisions) — structural glue, subtle but visible
  if (type === "temporal") {
    return Object.assign(base, {
      color: { color: "#58a6ff", highlight: "#79c0ff", opacity: 0.25 },
      width: 0.8,
    });
  }
  return base;
}

function renderGraph(g) {
  if (!g || !g.nodes) return;
  renderGraphLegend();
  const canvas = $("graph-canvas");
  const visNodes = g.nodes.map(n => {
    const style = nodeStyle(n.type);
    graphNodeById[n.id] = n;
    return Object.assign({
      id: n.id,
      label: n.type === "current" ? n.label : "",
      title: n.full,   // tooltip
      type: n.type,
    }, style);
  });
  const visEdges = g.edges.map((e, i) => Object.assign(
    { id: `e${i}`, from: e.from, to: e.to, type: e.type },
    edgeStyle(e.type, e.weight || 1, !!e.current),
  ));

  const stats = g.stats || {};
  $("graph-stats").textContent = `${stats.decisions||0} decisions · ${stats.docs||0} docs · ${stats.prompts||0} prompts · ${stats.edges||0} edges`;

  if (graphNetwork) {
    graphNetwork.setData({ nodes: visNodes, edges: visEdges });
    return;
  }

  const data = {
    nodes: new vis.DataSet(visNodes),
    edges: new vis.DataSet(visEdges),
  };
  // Per-edge physics: temporal edges have short tight springs (cluster same-day
  // decisions together); topic edges medium; retrieval edges long (radial cone).
  visEdges.forEach(e => {
    if (e.type === "temporal")       { e.length = 55;  e.physics = true; }
    else if (e.type === "topic")     { e.length = 140; e.physics = true; }
    else if (e.type === "recall-d")  { e.length = 220; e.physics = true; }
    else if (e.type === "recall-w")  { e.length = 240; e.physics = true; }
  });

  const options = {
    interaction: { hover: true, hoverConnectedEdges: true, tooltipDelay: 80, dragView: true, zoomView: true },
    physics: {
      enabled: true,
      solver: "forceAtlas2Based",
      forceAtlas2Based: {
        gravitationalConstant: -65,    // stronger node repulsion → sharper cluster gaps
        centralGravity: 0.004,         // let clusters drift apart
        springLength: 110,
        springConstant: 0.11,          // tighter springs within connected nodes
        damping: 0.55,
        avoidOverlap: 0.3,
      },
      stabilization: { iterations: 320, fit: true },
      maxVelocity: 60,
    },
    nodes: { borderWidth: 1.5, shadow: false },
    edges: { selectionWidth: 2.5 },
  };

  graphNetwork = new vis.Network(canvas, data, options);

  graphNetwork.on("click", (params) => {
    const detail = $("graph-detail");
    if (params.nodes.length === 0) {
      detail.classList.add("empty");
      detail.innerHTML = "";
      return;
    }
    const id = params.nodes[0];
    const n = graphNodeById[id];
    if (!n) return;
    detail.classList.remove("empty");
    const meta = [];
    if (n.date) meta.push(`date: ${esc(n.date)}`);
    if (n.ts)   meta.push(`ts: ${esc(fmtTs(n.ts))}`);
    detail.innerHTML = `
      <div class="node-info">
        <span class="tag ${esc(n.type)}">${esc(n.type)}</span>
        <span class="full">${esc(n.full)}</span>
        ${meta.length ? `<div class="meta">${meta.join(" · ")}</div>` : ""}
      </div>`;
  });
}

function refreshGraph() {
  fetch("/api/graph").then(r => r.json()).then(renderGraph).catch(console.error);
}

function renderSamples(samples) {
  const host = $("samples");
  const ageEl = $("samples-age");
  if (!samples || !samples.prompts || samples.prompts.length === 0) {
    host.innerHTML = `<div style="color:var(--text-dim); padding:12px; font-family:var(--mono); font-size:12px;">Computing samples… (first run can take ~1-2s)</div>`;
    ageEl.textContent = "";
    return;
  }
  const ageSec = Math.max(0, Math.round(Date.now()/1000 - samples.computed_at));
  ageEl.textContent = `computed ${ageSec}s ago`;
  host.innerHTML = samples.prompts.map(p => `
    <div class="sample">
      <div class="q">
        <span class="ts">${esc(fmtTs(p.ts))}</span>
        <span class="prompt">${esc(p.preview)}</span>
      </div>
      <div class="blocks">
        ${renderCmBlock(p.cm)}
        ${renderBlock("G1", "decisions", p.g1)}
        ${renderBlock("G2-DOCS", "BM25 docs", p.g2_docs)}
        ${renderBlock("G2-PREFETCH", "code graph", p.g2_prefetch)}
      </div>
    </div>
  `).join("");
}

function renderEvents(evs) {
  if (!evs || evs.length === 0) return `<div style="color:var(--text-dim); padding:10px;">No recent events.</div>`;
  return evs.map(e => `
    <div class="ev">
      <div class="t">${esc(e.time)}</div>
      <div class="ty">${esc(e.type)}</div>
      <div class="hk">${esc(e.hook || "")}</div>
      <div class="bk">${esc(e.block || "")}</div>
      <div class="dur">${e.duration_ms != null ? esc(e.duration_ms) + "ms" : ""}</div>
    </div>`).join("");
}

function renderActivity(activity) {
  const xs = activity.map(a => a.ts);
  const ys = activity.map(a => a.count);
  const opts = {
    width: $("activity-chart").clientWidth,
    height: 160,
    scales: { x: { time: true } },
    axes: [
      { stroke: "#7d8590", grid: { stroke: "rgba(255,255,255,0.04)" } },
      { stroke: "#7d8590", grid: { stroke: "rgba(255,255,255,0.04)" } },
    ],
    series: [
      {},
      {
        label: "events/min",
        stroke: "#58a6ff",
        fill: "rgba(88,166,255,0.15)",
        width: 2,
        points: { show: false },
      },
    ],
  };
  if (activityPlot) {
    activityPlot.setData([xs, ys]);
  } else {
    activityPlot = new uPlot(opts, [xs, ys], $("activity-chart"));
  }
}

function apply(snap) {
  if (snap.empty) {
    $("meta").textContent = snap.message || "no events";
    return;
  }
  $("meta").textContent = `${snap.total_events} events · window ${snap.window}`;
  $("updated").textContent = `Updated ${snap.updated}`;
  $("window").textContent = snap.window;
  const grade = $("grade");
  grade.textContent = snap.grade.label;
  grade.className = "grade " + snap.grade.style;
  $("health-rows").innerHTML = snap.rows.map(renderHealthRow).join("");
  renderActivity(snap.activity);
  $("latency-bars").innerHTML = renderLatencyBars(snap.latency_hist);
  renderUtility(snap.utility);
  $("notices").innerHTML = renderNotices(snap.notices);
  $("other").innerHTML = renderOther(snap.other);
  $("events").innerHTML = renderEvents(snap.recent);
  renderSamples(snap.samples);
  $("thresholds").textContent = fmtThresholds(snap.thresholds);

  // Reactive graph refresh: when total_events grows, a new user prompt/hook
  // fired — re-fetch the graph so the current-prompt node and its retrieval
  // cone update in near-realtime (lag ≈ one SSE tick + one graph rebuild).
  if (snap.total_events > lastEventCount) {
    lastEventCount = snap.total_events;
    // Skip the very first call (initial load already triggered refreshGraph())
    if (lastEventCount > 0 && graphNetwork) {
      setTimeout(refreshGraph, 400);  // small delay so samples recompute in parallel
    }
  }
}

// Refresh buttons — samples + graph
document.addEventListener("click", async (e) => {
  if (!e.target) return;
  if (e.target.id === "refresh-samples") {
    const btn = e.target;
    btn.disabled = true; btn.textContent = "…";
    try { await fetch("/api/samples/refresh", { method: "POST" }); }
    catch (err) { console.error(err); }
    setTimeout(() => { btn.disabled = false; btn.textContent = "refresh"; }, 2000);
  } else if (e.target.id === "refresh-graph") {
    const btn = e.target;
    btn.disabled = true; btn.textContent = "…";
    try {
      await fetch("/api/graph/refresh", { method: "POST" });
      refreshGraph();
    } catch (err) { console.error(err); }
    setTimeout(() => { btn.disabled = false; btn.textContent = "refresh"; }, 2000);
  }
});

function connect() {
  const status = $("conn-status");
  const es = new EventSource("/stream");
  es.onmessage = (e) => {
    status.textContent = "live"; status.className = "conn ok";
    try { apply(JSON.parse(e.data)); } catch (err) { console.error(err); }
  };
  es.onerror = () => {
    status.textContent = "reconnecting…"; status.className = "conn err";
  };
}

// Initial fetch so the page is never blank while waiting for SSE
fetch("/api/snapshot").then(r => r.json()).then(apply).catch(console.error);
connect();

// Initial graph load
refreshGraph();

// Re-render chart on resize
window.addEventListener("resize", () => {
  if (activityPlot) {
    activityPlot.setSize({ width: $("activity-chart").clientWidth, height: 160 });
  }
});
