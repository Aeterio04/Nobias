// ── Model Results — Fixed to read serialized report fields ──
import { getState } from '../store.js';

export function modelResultsPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  const result = state.modelResult;
  
  if (!result) {
    d.innerHTML = '<div style="padding:40px;text-align:center;color:var(--c-text-4)">No model audit results available. <a href="#/model-upload">Run an audit</a></div>';
    return d;
  }
  
  const severity = (result.overall_severity || 'UNKNOWN').toUpperCase();
  const severityClass = severity.toLowerCase();
  
  // Build scorecard metrics from the scorecard dict
  const scorecard = result.scorecard || {};
  const scorecardEntries = Object.entries(scorecard);
  
  // Build findings
  const findings = result.findings || [];
  const criticalCount = findings.filter(f => {
    const s = typeof f.severity === 'string' ? f.severity : (f.severity?.value || '');
    return s.toUpperCase() === 'CRITICAL';
  }).length;
  
  // Counterfactual data
  const cf = result.counterfactual || {};
  const flipRate = cf.flip_rate;
  const flipsByAttr = cf.flips_by_attribute || {};
  
  // Mitigation options
  const mitigations = result.mitigation_options || [];
  
  d.innerHTML = `
    <div class="verdict verdict-${severityClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severity} BIAS DETECTED</div>
        <div class="verdict-stats">${findings.length} findings${criticalCount > 0 ? ` · <span style="color:var(--c-critical)">${criticalCount} critical</span>` : ''}</div>
        <div class="verdict-meta" style="margin-top:8px">Model: <code class="mono" style="font-size:12px">${result.model_name || 'Unknown'}</code></div>
      </div>
      <div class="verdict-actions">
        <button class="btn btn-secondary btn-sm" id="export-json-btn">Export JSON</button>
      </div>
    </div>
    
    ${flipRate != null ? `
    <div class="section anim-2 mt-8">
      <div class="section-title mb-4">Counterfactual Analysis</div>
      <div class="card">
        <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:16px">
          <span style="font-size:32px;font-weight:700;letter-spacing:-0.03em;color:${flipRate > 0.10 ? 'var(--c-critical)' : flipRate > 0.05 ? 'var(--c-moderate)' : 'var(--c-clear)'}">${(flipRate * 100).toFixed(1)}%</span>
          <span style="font-size:14px;color:var(--c-text-3)">Counterfactual Flip Rate</span>
        </div>
        <p style="font-size:13px;color:var(--c-text-4);margin-bottom:16px">Percentage of predictions that change when protected attributes are swapped while keeping all other features constant.</p>
        ${Object.keys(flipsByAttr).length > 0 ? `
        <div style="display:flex;gap:24px;flex-wrap:wrap">
          ${Object.entries(flipsByAttr).map(([attr, count]) => `
            <div style="padding:12px 20px;background:var(--c-bg-elevated);border-radius:8px">
              <div style="font-size:12px;color:var(--c-text-4);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">${attr}</div>
              <div style="font-size:20px;font-weight:600;color:var(--c-text-1)">${count} flips</div>
            </div>
          `).join('')}
        </div>` : ''}
      </div>
    </div>` : ''}
    
    <div class="section anim-2 mt-8">
      <div class="section-title mb-6">Fairness Scorecard</div>
      ${scorecardEntries.length > 0 ? `
      <div class="table-container">
        <table class="table">
          <thead><tr><th>METRIC</th><th>GROUPS</th><th>VALUE</th><th>THRESHOLD</th><th>STATUS</th></tr></thead>
          <tbody>
            ${scorecardEntries.map(([key, m]) => {
              const passedClass = m.passed ? 'clear' : 'critical';
              const statusText = m.passed ? 'PASSED' : 'FAILED';
              return `<tr class="row-${passedClass}">
                <td style="font-weight:500">${m.metric_name || key}</td>
                <td style="font-size:12px;color:var(--c-text-4)">${m.privileged_group || '—'} vs ${m.unprivileged_group || '—'}</td>
                <td class="mono" style="color:${m.passed ? 'var(--c-clear)' : 'var(--c-critical)'}">${m.value != null ? Number(m.value).toFixed(4) : '—'}</td>
                <td class="mono" style="font-size:12px;color:var(--c-text-4)">${m.threshold != null ? Number(m.threshold).toFixed(2) : '—'}</td>
                <td><span class="badge badge-${passedClass}">${statusText}</span></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>` : '<div style="padding:24px;text-align:center;color:var(--c-text-4)">No scorecard metrics available</div>'}
    </div>
    
    ${findings.length > 0 ? `
    <div class="section anim-3 mt-10">
      <div class="section-title mb-4">Findings</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>ID</th><th>SEVERITY</th><th>FINDING</th><th>CATEGORY</th><th>AFFECTED GROUPS</th></tr></thead>
          <tbody>
            ${findings.map(f => {
              const fSev = typeof f.severity === 'string' ? f.severity.toUpperCase() : (f.severity?.value || 'LOW').toUpperCase();
              return `<tr class="row-${fSev.toLowerCase()}">
                <td class="mono" style="font-size:12px">${f.finding_id || '—'}</td>
                <td><span class="badge badge-${fSev.toLowerCase()}">${fSev}</span></td>
                <td>
                  <div style="font-weight:500">${f.title || '—'}</div>
                  <div style="font-size:12px;color:var(--c-text-4);margin-top:4px">${f.description || ''}</div>
                </td>
                <td style="font-size:12px;color:var(--c-text-3)">${f.category || '—'}</td>
                <td>${(f.affected_groups || []).map(g => `<span class="chip" style="font-size:11px">${g}</span>`).join(' ') || '—'}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>` : ''}
    
    ${mitigations.length > 0 ? `
    <div class="section anim-4 mt-10">
      <div class="section-title mb-4">Mitigation Strategies</div>
      <div class="suggested-fixes">
        ${mitigations.map((m, i) => `
          <div class="fix-card">
            <span class="fix-number">${i + 1}</span>
            <h4>${m.strategy_name || 'Strategy'}</h4>
            <div style="display:flex;gap:8px;margin:8px 0">
              <span class="badge badge-${m.implementation_complexity === 'low' ? 'clear' : m.implementation_complexity === 'high' ? 'critical' : 'moderate'}" style="font-size:11px">${(m.implementation_complexity || '').toUpperCase()} COMPLEXITY</span>
              <span class="badge" style="font-size:11px;background:var(--c-bg-elevated);color:var(--c-text-3)">${m.category || ''}</span>
              ${m.requires_retraining ? '<span class="badge badge-warn" style="font-size:11px">REQUIRES RETRAINING</span>' : ''}
            </div>
            <p>${m.description || ''}</p>
            ${m.expected_impact ? `<div style="font-size:13px;color:var(--c-text-3);margin-top:8px">Expected impact: ${m.expected_impact}</div>` : ''}
            ${m.code_example ? `<details style="margin-top:8px"><summary style="font-size:12px;color:var(--c-accent);cursor:pointer">View Code Example</summary><pre style="margin-top:8px;padding:12px;background:var(--c-bg-elevated);border-radius:6px;font-size:11px;overflow-x:auto"><code>${m.code_example}</code></pre></details>` : ''}
          </div>
        `).join('')}
      </div>
    </div>` : ''}
    
    <div class="anim-5 mt-8" style="text-align:center">
      <button class="btn btn-secondary" onclick="navigate('model-upload')">← Run Another Audit</button>
    </div>
  `;
  
  // Wire export
  setTimeout(() => {
    d.querySelector('#export-json-btn')?.addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `nobias_model_audit_${result.audit_id || 'export'}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }, 0);
  
  return d;
}
