// ── Model Results — Redesigned ──
import { getState } from '../store.js';

export function modelResultsPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  const result = state.modelResult;
  
  if (!result) {
    d.innerHTML = '<div style="padding:40px;text-align:center;color:var(--c-text-4)">No model audit results available. <a href="#/model-upload">Run an audit</a></div>';
    return d;
  }
  
  const severityClass = result.overall_severity || 'moderate';
  const severityText = (result.overall_severity || 'moderate').toUpperCase();
  
  d.innerHTML = `
    <div class="anim-1"><div class="tabs"><button class="tab active">Overview</button><button class="tab">Metrics</button><button class="tab">Findings</button></div></div>
    <div class="verdict verdict-${severityClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severityText} BIAS DETECTED</div>
        <div class="verdict-stats">${result.finding_count || 0} findings</div>
        <div class="verdict-meta" style="margin-top:8px">Model: <code class="mono" style="font-size:12px">${result.model_name || 'Unknown'}</code></div>
      </div>
      <div class="verdict-actions"><button class="btn btn-secondary btn-sm">Export PDF</button><button class="btn btn-secondary btn-sm">Export JSON</button></div>
    </div>
    <div class="section anim-2">
      <div class="section-title mb-6">Fairness Metrics</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>METRIC</th><th>VALUE</th><th>THRESHOLD</th><th>STATUS</th></tr></thead>
          <tbody>
            ${(result.metrics || []).map(m => `
              <tr class="row-${m.status}">
                <td style="font-weight:500">${m.name}</td>
                <td class="mono">${m.value}</td>
                <td class="mono" style="font-size:12px;color:var(--c-text-4)">${m.threshold}</td>
                <td><span class="badge badge-${m.status}">${m.status.toUpperCase()}</span></td>
              </tr>
            `).join('') || '<tr><td colspan="4" style="text-align:center;color:var(--c-text-4)">No metrics available</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
  `;
  
  return d;
}
