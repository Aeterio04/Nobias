// ── Dashboard Page — Redesigned ──
import { api } from '../api.js';
import { getState, setState } from '../store.js';

const datasetIcon = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg>';
const modelIcon = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>';
const agentIcon = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M10 14h.01M14 14h.01"/></svg>';

export function dashboardPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Welcome to Nobias</h1>
      <p class="page-subtitle">Choose an auditor to get started. Detect, measure, and fix bias in your AI systems.</p>
    </div>

    <div class="dashboard-stats anim-2">
      <div class="stat-card">
        <div class="stat-label">TOTAL AUDITS</div>
        <div class="stat-value" id="total-audits">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">CRITICAL FINDINGS</div>
        <div class="stat-value" style="color:var(--c-critical)" id="critical-count">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">LAST AUDIT</div>
        <div class="metric-md" id="last-audit">Never</div>
      </div>
    </div>

    <div class="dashboard-modules anim-3">
      <div class="module-card" onclick="navigate('dataset-upload')">
        <div class="module-card-icon" style="background:var(--c-accent-bg);color:var(--c-accent)">${datasetIcon}</div>
        <h3>Dataset Auditor</h3>
        <p>Audit raw datasets for representation bias and statistical anomalies before training.</p>
        <div class="module-card-tags">
          <span class="format-badge">CSV</span><span class="format-badge">XLSX</span><span class="format-badge">Parquet</span>
        </div>
        <button class="btn btn-primary btn-full" onclick="event.stopPropagation();navigate('dataset-upload')">Start Audit →</button>
      </div>

      <div class="module-card" onclick="navigate('model-upload')">
        <div class="module-card-icon" style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet)">${modelIcon}</div>
        <h3>Model Auditor</h3>
        <p>Audit trained ML models for fairness, disparate impact, and performance parity.</p>
        <div class="module-card-tags">
          <span class="format-badge">.pkl</span><span class="format-badge">.onnx</span><span class="format-badge">.joblib</span><span class="format-badge">.h5</span>
        </div>
        <button class="btn btn-violet btn-full" onclick="event.stopPropagation();navigate('model-upload')">Start Audit →</button>
      </div>

      <div class="module-card" onclick="navigate('agent-setup')">
        <div style="display:flex;justify-content:space-between;align-items:start;width:100%">
          <div class="module-card-icon" style="background:var(--c-accent-teal-bg);color:var(--c-accent-teal)">${agentIcon}</div>
          <span class="badge badge-warn" style="font-size:11px;letter-spacing:0.05em">MOST COMPLEX</span>
        </div>
        <h3>Agent Auditor</h3>
        <p>Audit LLM-powered agents for alignment, toxicity, and edge-case behaviors.</p>
        <div class="module-card-tags">
          <span class="format-badge">GPT-4o</span><span class="format-badge">Claude</span><span class="format-badge">Ollama</span>
        </div>
        <button class="btn btn-teal btn-full" onclick="event.stopPropagation();navigate('agent-setup')">Start Audit →</button>
      </div>
    </div>

    <div class="section anim-4">
      <div class="section-title mb-4">Recent Audits</div>
      <div id="history-container">
        <div style="text-align:center;padding:40px;color:var(--c-text-4)">Loading history...</div>
      </div>
    </div>
  `;
  
  setTimeout(async () => {
    try {
      const history = await api.history.list();
      setState({ history });
      
      const totalAudits = history.length;
      const criticalCount = history.filter(h => h.severity === 'critical').length;
      const lastAudit = history.length > 0 ? new Date(history[0].timestamp).toLocaleString() : 'Never';
      
      d.querySelector('#total-audits').textContent = totalAudits;
      d.querySelector('#critical-count').textContent = criticalCount;
      d.querySelector('#last-audit').textContent = lastAudit;
      
      const historyContainer = d.querySelector('#history-container');
      if (history.length === 0) {
        historyContainer.innerHTML = '<div style="text-align:center;padding:40px;color:var(--c-text-4)">No audits yet. Start your first audit above!</div>';
      } else {
        const typeIcons = { dataset: datasetIcon, model: modelIcon, agent: agentIcon };
        const typeColors = { dataset: 'var(--c-accent)', model: 'var(--c-accent-violet)', agent: 'var(--c-accent-teal)' };
        const typeBgs = { dataset: 'var(--c-accent-bg)', model: 'var(--c-accent-violet-bg)', agent: 'var(--c-accent-teal-bg)' };
        
        historyContainer.innerHTML = `
          <div class="table-container">
            <table class="table">
              <thead><tr><th>TYPE</th><th>AUDIT NAME</th><th>DATE</th><th>STATUS</th><th>ACTION</th></tr></thead>
              <tbody>
                ${history.slice(0, 10).map(h => `
                  <tr class="row-${h.severity}">
                    <td><div style="width:28px;height:28px;border-radius:6px;background:${typeBgs[h.audit_type]};display:flex;align-items:center;justify-content:center;color:${typeColors[h.audit_type]}">${typeIcons[h.audit_type]}</div></td>
                    <td style="font-weight:500;color:var(--c-text-1)">${h.name}</td>
                    <td style="color:var(--c-text-4);font-size:13px">${new Date(h.timestamp).toLocaleString()}</td>
                    <td><span class="badge badge-${h.severity}">${h.severity.toUpperCase()}</span></td>
                    <td><a href="#/${h.audit_type}-results" class="btn-ghost">View Results</a></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
    } catch (err) {
      console.error('Failed to load history:', err);
      d.querySelector('#history-container').innerHTML = '<div style="text-align:center;padding:40px;color:var(--c-critical)">Failed to load history</div>';
    }
  }, 0);
  
  return d;
}
