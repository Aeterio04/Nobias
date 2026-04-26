// ── Agent Results — Redesigned ──
import { getState } from '../store.js';

export function agentResultsPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  const result = state.agentResult;
  
  if (!result) {
    d.innerHTML = '<div style="padding:40px;text-align:center;color:var(--c-text-4)">No agent audit results available. <a href="#/agent-setup">Run an audit</a></div>';
    return d;
  }
  
  const severityClass = result.overall_severity || 'moderate';
  const severityText = (result.overall_severity || 'moderate').toUpperCase();
  
  d.innerHTML = `
    <div class="verdict verdict-${severityClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severityText} BIAS DETECTED</div>
        <div style="font-size:28px;font-weight:700;letter-spacing:-0.03em;color:var(--c-text-1);margin:8px 0">Overall CFR: ${result.overall_cfr || 'N/A'}</div>
        <div class="verdict-stats">${result.finding_count || 0} findings · ${result.api_calls || 0} API calls</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;flex-shrink:0">
        <button class="btn btn-secondary btn-sm">Export PDF</button>
        <button class="btn btn-secondary btn-sm">Export JSON</button>
      </div>
    </div>
    <div class="section anim-2">
      <div class="section-title mb-4">Audit Findings</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>SEVERITY</th><th>FINDING</th><th>ATTRIBUTE</th><th>CFR</th></tr></thead>
          <tbody>
            ${(result.findings || []).map(f => `
              <tr class="row-${f.severity}">
                <td><span class="badge badge-${f.severity}">${f.severity.toUpperCase()}</span></td>
                <td>${f.description}</td>
                <td><code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 6px;border-radius:3px">${f.attribute}</code></td>
                <td class="mono" style="color:var(--c-${f.severity})">${f.cfr || 'N/A'}</td>
              </tr>
            `).join('') || '<tr><td colspan="4" style="text-align:center;color:var(--c-text-4)">No findings</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
  `;
  
  return d;
}
