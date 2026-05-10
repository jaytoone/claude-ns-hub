/* Entity Corpus Dashboard — app.js */

const $ = id => document.getElementById(id);
const tbody = $('corpus-tbody');
const detailPanel = $('detail-panel');
const detailTitle = $('detail-title');
const detailBody = $('detail-body');
const missPanel = $('miss-panel');
const missTbody = $('miss-tbody');

// Domain hierarchy definition — matches SKILL.md Domain Hierarchy
const DOMAIN_HIERARCHY = [
  { key: 'demand_theory',  icon: '◈', label: 'Demand Theory',    desc: 'WHY people buy' },
  { key: 'go_to_market',   icon: '◉', label: 'Go-To-Market',     desc: 'HOW to reach market' },
  { key: 'product',        icon: '◎', label: 'Product',          desc: 'WHAT to build' },
  { key: 'research',       icon: '◇', label: 'Research',         desc: 'HOW to know' },
];

let state = {
  corpora: [],
  selected: null,
  sortCol: 'name',
  sortDir: 1,
  collapsedGroups: new Set(),
  viewMode: 'grouped',   // 'grouped' | 'flat'
};

// ── SSE connection ────────────────────────────────────────────────────────────

function connect() {
  const es = new EventSource('/stream');
  es.onmessage = e => {
    try { render(JSON.parse(e.data)); } catch (_) {}
  };
  es.onerror = () => {
    setTimeout(connect, 3000);
  };
}

// ── Render ────────────────────────────────────────────────────────────────────

let _lastCorporaHash = null;
let _lastMissHash = null;

function render(data) {
  const s = data.summary;

  // Always update the timestamp (non-blinking text node, no repaint)
  $('updated-ts').textContent = s.updated;

  // Stats bar — only update if values changed
  const newStats = `${s.total}|${s.stable}|${s.draft}|${s.total_docs}`;
  if ($('stat-total').dataset.val !== newStats) {
    $('stat-total').textContent = s.total;
    $('stat-stable').textContent = s.stable;
    $('stat-draft').textContent = s.draft;
    $('stat-docs').textContent = s.total_docs;
    $('stat-total').dataset.val = newStats;
  }

  // Table — skip DOM rebuild if corpus data is identical
  const corporaHash = JSON.stringify(data.corpora.map(c =>
    `${c.name}:${c.status}:${c.doc_count}:${c.file_count}:${c.last_modified_str}:${c.root_exists}`
  ));
  if (corporaHash !== _lastCorporaHash) {
    _lastCorporaHash = corporaHash;
    state.corpora = data.corpora;
    renderTable();
  }

  // Miss log — skip if unchanged
  const missHash = JSON.stringify(data.miss_log || {});
  if (missHash !== _lastMissHash) {
    _lastMissHash = missHash;
    renderMissLog(data.miss_log || {});
  }
}

function corpusRowHtml(c, inGroup = false) {
  const statusBadge = `<span class="badge ${c.status}">${c.status}</span>`;

  let filesHtml;
  if (c.doc_count === 0) {
    filesHtml = `<span class="file-count" style="color:var(--text-dim)">—</span>`;
  } else if (c.file_match) {
    filesHtml = `<span class="file-count ok">${c.file_count}</span>`;
  } else if (c.file_count === 0) {
    filesHtml = `<span class="file-count missing">0/${c.doc_count}</span>`;
  } else {
    filesHtml = `<span class="file-count mismatch">${c.file_count}/${c.doc_count}</span>`;
  }

  const tiers = Object.entries(c.taxonomy_groups || {})
    .map(([g, ids]) => `<span class="tier-pill">${g}:${ids.length}</span>`)
    .join('');

  const rootBadge = c.root_exists
    ? `<span class="root-badge ok">OK</span>`
    : `<span class="root-badge missing">!</span>`;

  // Layer badge
  const layerColor = c.layer === 'L1' ? 'var(--accent)' : c.layer === 'L2' ? 'var(--blue)' : 'var(--text-dim)';
  const layerBadge = `<span style="font-family:var(--mono);font-size:11px;font-weight:500;color:${layerColor}">${esc(c.layer)}</span>`;

  // Age / staleness
  const STALE_COLOR = { fresh: 'var(--green)', aging: 'var(--yellow)', stale: 'var(--red)', unknown: 'var(--text-dim)' };
  const ageLabel = c.days_old !== null && c.days_old !== undefined ? `${c.days_old}d` : '—';
  const ageHtml = `<span style="font-family:var(--mono);font-size:11px;color:${STALE_COLOR[c.staleness] || 'var(--text-dim)'}" title="${c.staleness}">${ageLabel}</span>`;

  const sel = state.selected === c.name ? 'selected' : '';
  const groupClass = inGroup ? 'in-group' : '';
  const prefix = inGroup ? `<span class="indent-arrow">└</span>` : '';
  return `<tr class="${sel} ${groupClass}" data-name="${esc(c.name)}">
    <td>${prefix}<span class="name-cell">${esc(c.name)}</span></td>
    <td>${statusBadge}</td>
    <td>${layerBadge}</td>
    <td style="font-size:12px;color:var(--text-dim);max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(c.domain)}">${esc(c.domain)}</td>
    <td style="font-family:var(--mono);font-size:12px">${c.doc_count}</td>
    <td>${filesHtml}</td>
    <td><div class="tier-pills">${tiers}</div></td>
    <td>${ageHtml}</td>
    <td>${rootBadge}</td>
  </tr>`;
}

function renderTable() {
  const html = [];

  // Group mode: render by DOMAIN_HIERARCHY order
  // Any domain not in DOMAIN_HIERARCHY goes to an "Other" group at the end
  const grouped = new Map();
  for (const d of DOMAIN_HIERARCHY) grouped.set(d.key, []);
  grouped.set('__other__', []);

  for (const c of state.corpora) {
    const key = DOMAIN_HIERARCHY.find(d => d.key === c.primary_domain) ? c.primary_domain : '__other__';
    grouped.get(key).push(c);
  }

  // Within each group, sort by sortCol
  for (const [, list] of grouped) {
    list.sort((a, b) => {
      let av = a[state.sortCol] ?? '', bv = b[state.sortCol] ?? '';
      if (typeof av === 'boolean') av = av ? 1 : 0;
      if (typeof bv === 'boolean') bv = bv ? 1 : 0;
      if (av < bv) return -state.sortDir;
      if (av > bv) return state.sortDir;
      return 0;
    });
  }

  const domainsToRender = [...DOMAIN_HIERARCHY.map(d => d.key), '__other__'];

  for (const domainKey of domainsToRender) {
    const list = grouped.get(domainKey) || [];
    if (list.length === 0) continue;

    const meta = DOMAIN_HIERARCHY.find(d => d.key === domainKey) ||
                 { key: domainKey, icon: '◌', label: 'Other', desc: '' };
    const collapsed = state.collapsedGroups.has(domainKey);
    const colClass = collapsed ? 'collapsed' : '';

    html.push(`<tr class="group-row ${colClass}" data-group="${esc(domainKey)}">
      <td colspan="8">
        <div class="group-header">
          <span class="group-icon">${meta.icon}</span>
          <span class="group-name">${esc(meta.label)}</span>
          <span class="group-desc">${esc(meta.desc)}</span>
          <span class="group-count">${list.length}</span>
          <span class="group-chevron">▾</span>
        </div>
      </td>
    </tr>`);

    if (!collapsed) {
      for (const c of list) {
        html.push(corpusRowHtml(c, true));
      }
    }
  }

  tbody.innerHTML = html.join('');

  // Corpus row click → detail
  tbody.querySelectorAll('tr[data-name]').forEach(tr => {
    tr.addEventListener('click', () => {
      const name = tr.dataset.name;
      if (state.selected === name) {
        closeDetail();
      } else {
        state.selected = name;
        renderTable();
        renderDetail(name);
      }
    });
  });

  // Group header click → collapse/expand
  tbody.querySelectorAll('tr.group-row').forEach(tr => {
    tr.addEventListener('click', () => {
      const key = tr.dataset.group;
      if (state.collapsedGroups.has(key)) {
        state.collapsedGroups.delete(key);
      } else {
        state.collapsedGroups.add(key);
      }
      renderTable();
    });
  });

  // Sort header arrows
  document.querySelectorAll('.corpus-table th[data-col]').forEach(th => {
    th.classList.toggle('sorted', th.dataset.col === state.sortCol);
    const arrow = th.querySelector('.sort-arrow');
    if (arrow) arrow.textContent = th.dataset.col === state.sortCol
      ? (state.sortDir === 1 ? '↑' : '↓') : '↕';
  });
}

function renderMissLog(missLog) {
  const entries = Object.entries(missLog);
  if (entries.length === 0) {
    missPanel.style.display = 'none';
    return;
  }
  missPanel.style.display = '';
  const rows = entries.map(([domain, entry]) => {
    const count = typeof entry === 'object' ? (entry.count || 0) : 0;
    const built = typeof entry === 'object' ? (entry.auto_corpus_triggered || false) : false;
    const countClass = count >= 2 ? 'high' : 'low';
    const actionHtml = built
      ? `<span class="action-pill built">built</span>`
      : `<span class="action-pill create" title="Use /entity -cc ${esc(domain)}">-cc ${esc(domain)}</span>`;
    return `<tr>
      <td style="font-family:var(--mono)">${esc(domain)}</td>
      <td><span class="miss-count ${countClass}">${count}× missed</span></td>
      <td>${actionHtml}</td>
    </tr>`;
  });
  missTbody.innerHTML = rows.join('');
}

async function renderDetail(name) {
  detailTitle.textContent = name;
  detailBody.innerHTML = `<div style="padding:20px;color:var(--text-dim)">Loading…</div>`;
  detailPanel.classList.add('open');

  let c;
  try {
    const res = await fetch(`/api/corpus/${encodeURIComponent(name)}`);
    c = await res.json();
  } catch (e) {
    detailBody.innerHTML = `<div style="padding:20px;color:var(--red)">Failed to load detail.</div>`;
    return;
  }

  // Docs section
  const docRows = Object.entries(c.docs || {}).map(([id, file]) => {
    const group = Object.entries(c.taxonomy_groups || {})
      .find(([, ids]) => ids.includes(id))?.[0] || '?';
    return `<li>
      <span class="doc-id">${esc(id)}</span>
      <span class="doc-group">${esc(group)}</span>
      <span class="doc-file" title="${esc(file)}">${esc(file)}</span>
    </li>`;
  }).join('');

  // Files on disk
  const fileRows = (c.file_listing || []).map(f =>
    `<li><span>${esc(f.name)}</span><span class="file-size">${(f.size / 1024).toFixed(1)} KB</span></li>`
  ).join('') || `<li style="color:var(--text-dim);font-style:italic">No files found</li>`;

  // Triggers
  const triggers = (c.triggers || []).slice(0, 6).map(t =>
    `<div class="trigger-item">${esc(t)}</div>`
  ).join('');

  // Core theory
  const theory = c.core_theory
    ? `<div class="theory-block">${esc(c.core_theory)}</div>`
    : `<span style="color:var(--text-dim);font-style:italic">Not available</span>`;

  // Root path
  const rootHtml = c.root_exists
    ? `<span class="root-badge ok">OK</span> <code style="font-size:11px;color:var(--text-dim)">${esc(c.corpus_root)}</code>`
    : `<span class="root-badge missing">MISSING</span> <code style="font-size:11px;color:var(--red)">${esc(c.corpus_root)}</code>`;

  detailBody.innerHTML = `
    <div class="detail-section">
      <h3>Info</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <tr><td style="color:var(--text-dim);width:110px;padding:3px 0">Status</td>
            <td><span class="badge ${esc(c.status)}">${esc(c.status)}</span></td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Domain</td>
            <td><span class="domain-tag ${esc(c.primary_domain)}">${esc(c.primary_domain)}</span></td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Layer</td>
            <td style="font-family:var(--mono)">${esc(c.layer)}</td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Description</td>
            <td style="color:var(--text-soft)">${esc(c.domain)}</td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Root</td>
            <td>${rootHtml}</td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Related</td>
            <td style="font-family:var(--mono);font-size:11px">${esc((c.related_domains || []).join(', ') || '—')}</td></tr>
        <tr><td style="color:var(--text-dim);padding:3px 0">Modified</td>
            <td style="font-family:var(--mono)">${esc(c.last_modified_str)}</td></tr>
      </table>

      <h3 style="margin-top:16px">Triggers</h3>
      <div class="trigger-list">${triggers}</div>

      <h3 style="margin-top:16px">Core Theory</h3>
      ${theory}
    </div>

    <div class="detail-section">
      <h3>Registered Docs (${c.doc_count})</h3>
      <ul class="doc-list">${docRows}</ul>

      <h3 style="margin-top:16px">Files on Disk</h3>
      <ul class="file-listing">${fileRows}</ul>
    </div>
  `;
}

function closeDetail() {
  state.selected = null;
  detailPanel.classList.remove('open');
  renderTable();
}

// ── Sort headers ──────────────────────────────────────────────────────────────

document.querySelectorAll('.corpus-table th[data-col]').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.col;
    if (state.sortCol === col) {
      state.sortDir *= -1;
    } else {
      state.sortCol = col;
      state.sortDir = 1;
    }
    renderTable();
  });
});

// ── Close detail ──────────────────────────────────────────────────────────────

$('detail-close').addEventListener('click', closeDetail);

// ── Escape HTML ───────────────────────────────────────────────────────────────

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Collapse / Expand all ─────────────────────────────────────────────────────

$('btn-collapse-all').addEventListener('click', () => {
  for (const d of DOMAIN_HIERARCHY) state.collapsedGroups.add(d.key);
  state.collapsedGroups.add('__other__');
  renderTable();
});

$('btn-expand-all').addEventListener('click', () => {
  state.collapsedGroups.clear();
  renderTable();
});

// ── Boot ──────────────────────────────────────────────────────────────────────

connect();
