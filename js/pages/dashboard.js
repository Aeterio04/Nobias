import { api } from '../api.js';
import { setState } from '../store.js';

const datasetIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg>`;
const modelIcon   = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg>`;
const agentIcon   = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 8V4H8"/><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M10 14h.01M14 14h.01"/></svg>`;
const trashIcon   = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>`;

const typeIcons  = { dataset: datasetIcon, model: modelIcon, agent: agentIcon };
const typeColors = { dataset: 'var(--c-accent)', model: 'var(--c-accent-violet)', agent: 'var(--c-accent-teal)' };
const typeBgs    = { dataset: 'var(--c-accent-bg)', model: 'var(--c-accent-violet-bg)', agent: 'var(--c-accent-teal-bg)' };

function fmtDate(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
      + ' ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  } catch { return ts; }
}

export function dashboardPage(nav) {
  const d = document.createElement('div');

  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Welcome to Nobias</h1>
      <p class="page-subtitle">Detect, measure, and fix bias in your AI systems.</p>
    </div>

    <div class="dashboard-stats anim-2">
      <div class="stat-card">
        <div class="stat-label">TOTAL AUDITS</div>
        <div class="stat-value" id="total-audits">—</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">CRITICAL FINDINGS</div>
        <div class="stat-value" style="color:var(--c-critical)" id="critical-count">—</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">LAST AUDIT</div>
        <div class="metric-md" id="last-audit">—</div>
      </div>
    </div>

    <div class="dashboard-modules anim-3">
      <div class="module-card" onclick="navigate('dataset-upload')">
        <div class="module-card-icon" style="background:var(--c-accent-bg);color:var(--c-accent)">${datasetIcon.replace('18','22').replace('18','22')}</div>
        <h3>Dataset Auditor</h3>
        <p>Audit raw datasets for representation bias and statistical anomalies before training.</p>
        <div class="module-card-tags"><span class="format-badge">CSV</span><span class="format-badge">XLSX</span><span class="format-badge">Parquet</span></div>
        <button class="btn btn-primary btn-full" onclick="event.stopPropagation();navigate('dataset-upload')">Start Audit →</button>
      </div>
      <div class="module-card" onclick="navigate('model-upload')">
        <div class="module-card-icon" style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet)">${modelIcon.replace('18','22').replace('18','22')}</div>
        <h3>Model Auditor</h3>
        <p>Audit trained ML models for fairness, disparate impact, and performance parity.</p>
        <div class="module-card-tags"><span class="format-badge">.pkl</span><span class="format-badge">.onnx</span><span class="format-badge">.joblib</span></div>
        <button class="btn btn-violet btn-full" onclick="event.stopPropagation();navigate('model-upload')">Start Audit →</button>
      </div>
      <div class="module-card" onclick="navigate('agent-setup')">
        <div style="display:flex;justify-content:space-between;align-items:start;width:100%">
          <div class="module-card-icon" style="background:var(--c-accent-teal-bg);color:var(--c-accent-teal)">${agentIcon.replace('18','22').replace('18','22')}</div>
          <span class="badge badge-warn" style="font-size:11px">MOST COMPLEX</span>
        </div>
        <h3>Agent Auditor</h3>
        <p>Audit LLM-powered agents for demographic bias using synthetic persona testing.</p>
        <div class="module-card-tags"><span class="format-badge">GPT-4o</span><span class="format-badge">Claude</span><span class="format-badge">Groq</span></div>
        <button class="btn btn-teal btn-full" onclick="event.stopPropagation();navigate('agent-setup')">Start Audit →</button>
      </div>
    </div>

    <div class="section anim-4">
      <div class="section-title mb-4">Recent Audits</div>
      <div id="history-container">
        <div style="display:flex;align-items:center;justify-content:center;gap:10px;padding:40px;color:var(--c-text-4)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          Loading history...
        </div>
      </div>
    </div>
  `;

  setTimeout(() => loadHistory(d, nav), 0);
  return d;
}

async function loadHistory(d, nav) {
  const container = d.querySelector('#history-container');
  try {
    const history = await api.history.list();
    setState({ history });

    d.querySelector('#total-audits').textContent  = history.length;
    d.querySelector('#critical-count').textContent = history.filter(h => (h.severity || '').toUpperCase() === 'CRITICAL').length;
    d.querySelector('#last-audit').textContent     = history.length > 0 ? fmtDate(history[0].timestamp) : 'Never';

    if (history.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--c-text-4)">No audits yet. Run your first audit above!</div>`;
      return;
    }

    renderHistoryTable(container, history, nav);
  } catch (err) {
    container.innerHTML = `
      <div style="text-align:center;padding:40px">
        <div style="color:var(--c-critical);margin-bottom:12px">Failed to load history. Is the backend running?</div>
        <button class="btn btn-secondary" id="retry-btn">Retry</button>
      </div>`;
    container.querySelector('#retry-btn').addEventListener('click', () => {
      container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--c-text-4)">Retrying...</div>`;
      loadHistory(d, nav);
    });
  }
}

function renderHistoryTable(container, history, nav) {
  const tbody = history.slice(0, 20).map(h => {
    const sev  = (h.severity || 'low').toLowerCase();
    const icon = typeIcons[h.audit_type]  || '';
    const bg   = typeBgs[h.audit_type]   || 'var(--c-bg-elevated)';
    const col  = typeColors[h.audit_type] || 'var(--c-text-3)';
    return `<tr class="row-${sev}" data-audit-id="${h.audit_id}" data-audit-type="${h.audit_type}" style="position:relative">
      <td>
        <div style="width:28px;height:28px;border-radius:6px;background:${bg};display:flex;align-items:center;justify-content:center;color:${col}">
          ${icon}
        </div>
      </td>
      <td style="font-weight:500;color:var(--c-text-1)">${h.name || 'Unknown'}</td>
      <td style="color:var(--c-text-4);font-size:13px">${fmtDate(h.timestamp)}</td>
      <td><span class="badge badge-${sev}">${(h.severity || 'UNKNOWN').toUpperCase()}</span></td>
      <td style="font-size:13px;color:var(--c-text-4)">${h.finding_count ?? '—'}</td>
      <td>
        <div style="display:flex;align-items:center;gap:8px">
          <button class="btn-ghost view-btn" data-audit-id="${h.audit_id}" data-audit-type="${h.audit_type}">View Results</button>
          <button class="delete-btn" data-audit-id="${h.audit_id}"
            style="opacity:0;background:none;border:none;cursor:pointer;color:var(--c-critical);padding:4px;border-radius:4px;display:flex;align-items:center;transition:opacity 0.15s">
            ${trashIcon}
          </button>
        </div>
      </td>
    </tr>`;
  }).join('');

  container.innerHTML = `
    <div class="table-container">
      <table class="table">
        <thead><tr><th>TYPE</th><th>AUDIT NAME</th><th>DATE</th><th>STATUS</th><th>FINDINGS</th><th>ACTION</th></tr></thead>
        <tbody id="history-tbody">${tbody}</tbody>
      </table>
    </div>`;

  // Show/hide delete button on row hover
  container.querySelectorAll('tr[data-audit-id]').forEach(row => {
    const delBtn = row.querySelector('.delete-btn');
    row.addEventListener('mouseenter', () => { if (delBtn) delBtn.style.opacity = '1'; });
    row.addEventListener('mouseleave', () => { if (delBtn) delBtn.style.opacity = '0'; });
  });

  // View Results — restore result into state then navigate
  container.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const auditId   = btn.dataset.auditId;
      const auditType = btn.dataset.auditType;
      try {
        const entry = await api.history.get(auditId);
        if (entry?.result) {
          if (auditType === 'dataset') setState({ datasetResult: entry.result });
          if (auditType === 'model')   setState({ modelResult:   entry.result });
          if (auditType === 'agent')   setState({ agentResult:   entry.result });
        }
        nav(`${auditType}-results`);
      } catch (err) {
        alert('Could not load audit: ' + err.message);
      }
    });
  });

  // Delete
  container.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const auditId = btn.dataset.auditId;
      try {
        await api.history.delete(auditId);
        const row = container.querySelector(`tr[data-audit-id="${auditId}"]`);
        row?.remove();
        // Update stats
        const remaining = container.querySelectorAll('tr[data-audit-id]').length;
        const totalEl = document.querySelector('#total-audits');
        if (totalEl) totalEl.textContent = remaining;
        if (remaining === 0) {
          container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--c-text-4)">No audits yet. Run your first audit above!</div>`;
        }
      } catch (err) {
        alert('Delete failed: ' + err.message);
      }
    });
  });
}
