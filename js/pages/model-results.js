import { getState } from '../store.js';

export function modelResultsPage(nav) {
  const d = document.createElement('div');
  const result = getState().modelResult;

  if (!result) {
    d.innerHTML = `
      <div style="padding:60px;text-align:center">
        <p style="font-size:16px;color:var(--c-text-4);margin-bottom:20px">
          No audit results found. Please run an audit first.
        </p>
        <button class="btn btn-secondary" onclick="navigate('model-upload')">← Go to Model Auditor</button>
      </div>`;
    return d;
  }

  const severity = (result.overall_severity || 'UNKNOWN').toUpperCase();
  const sevClass = { CRITICAL:'verdict-critical', MODERATE:'verdict-moderate', LOW:'verdict-low', CLEAR:'verdict-clear' }[severity] || 'verdict-moderate';

  // ── Counterfactual ───────────────────────────────────────────────────────
  const cf = result.counterfactual;
  const cfHTML = cf != null ? (() => {
    const flipRate = cf.flip_rate ?? 0;
    const flipColor = flipRate > 0.10 ? 'var(--c-critical)' : flipRate > 0.05 ? 'var(--c-moderate)' : 'var(--c-clear)';
    const byAttr = cf.flips_by_attribute || {};
    const hasAttrBreakdown = Object.keys(byAttr).length > 0 && Object.values(byAttr).some(v => v > 0);
    return `
    <div class="section anim-2 mt-8">
      <div class="section-title mb-4">Counterfactual Analysis</div>
      <div class="card">
        <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:12px">
          <span style="font-size:36px;font-weight:700;letter-spacing:-0.03em;color:${flipColor}">${cf.flip_rate_pct || (flipRate * 100).toFixed(1) + '%'}</span>
          <span style="font-size:14px;color:var(--c-text-3)">Counterfactual Flip Rate</span>
        </div>
        <p style="font-size:13px;color:var(--c-text-4);margin-bottom:${hasAttrBreakdown ? 16 : 0}px">
          Percentage of predictions that change when protected attributes are swapped while keeping all other features constant.
        </p>
        ${hasAttrBreakdown ? `
        <div style="display:flex;gap:16px;flex-wrap:wrap">
          ${Object.entries(byAttr).map(([attr, count]) => `
            <div style="padding:10px 18px;background:var(--c-bg-elevated);border-radius:8px">
              <div style="font-size:11px;color:var(--c-text-4);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">${attr}</div>
              <div style="font-size:18px;font-weight:600;color:var(--c-text-1)">${count} flips</div>
            </div>`).join('')}
        </div>` : ''}
      </div>
    </div>`;
  })() : '';

  // ── Scorecard ────────────────────────────────────────────────────────────
  const scorecard = result.scorecard || {};
  const validScorecard = Object.entries(scorecard).filter(([, m]) => m.value != null && !m.error);
  const scorecardHTML = `
    <div class="section anim-2 mt-8">
      <div class="section-title mb-4">Fairness Scorecard</div>
      ${validScorecard.length > 0 ? `
      <div class="table-container">
        <table class="table">
          <thead><tr><th>METRIC</th><th>GROUPS</th><th>VALUE</th><th>THRESHOLD</th><th>STATUS</th></tr></thead>
          <tbody>
            ${validScorecard.map(([, m]) => {
              const passed = m.passed;
              return `<tr class="row-${passed ? 'clear' : 'critical'}">
                <td style="font-weight:500">${m.metric_name || '—'}</td>
                <td style="font-size:12px;color:var(--c-text-4)">${m.privileged_group || '—'} vs ${m.unprivileged_group || '—'}</td>
                <td class="mono" style="color:${passed ? 'var(--c-clear)' : 'var(--c-critical)'}">${Number(m.value).toFixed(4)}</td>
                <td class="mono" style="font-size:12px;color:var(--c-text-4)">${m.threshold != null ? Number(m.threshold).toFixed(2) : '—'}</td>
                <td><span class="badge badge-${passed ? 'clear' : 'critical'}">${passed ? 'PASSED' : 'FAILED'}</span></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>` : '<div style="padding:24px;text-align:center;color:var(--c-text-4)">Scorecard data not available for this audit.</div>'}
    </div>`;

  // ── Findings ─────────────────────────────────────────────────────────────
  const findings = result.findings || [];
  const validFindings = findings.filter(f => f.severity && (f.title || f.description));
  const findingsHTML = `
    <div class="section anim-3 mt-10">
      <div class="section-title mb-4">Findings</div>
      ${validFindings.length > 0 ? `
      <div class="table-container">
        <table class="table">
          <thead><tr><th>ID</th><th>SEVERITY</th><th>FINDING</th><th>CATEGORY</th><th>AFFECTED GROUPS</th></tr></thead>
          <tbody>
            ${validFindings.map(f => {
              const sev = (f.severity || 'LOW').toUpperCase();
              return `<tr class="row-${sev.toLowerCase()}">
                <td class="mono" style="font-size:12px">${f.finding_id || '—'}</td>
                <td><span class="badge badge-${sev.toLowerCase()}">${sev}</span></td>
                <td>
                  <div style="font-weight:500">${f.title || '—'}</div>
                  ${f.description ? `<div style="font-size:12px;color:var(--c-text-4);margin-top:3px">${f.description}</div>` : ''}
                </td>
                <td style="font-size:12px;color:var(--c-text-3)">${f.category || '—'}</td>
                <td>${(f.affected_groups || []).map(g => `<span class="chip" style="font-size:11px">${g}</span>`).join(' ') || '—'}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>` : '<div style="padding:24px;text-align:center;color:var(--c-text-4)">No findings detected. This model passed all fairness checks.</div>'}
    </div>`;

  // ── Mitigations ───────────────────────────────────────────────────────────
  const mitigations = result.mitigation_options || [];
  const mitigationsHTML = mitigations.length > 0 ? `
    <div class="section anim-4 mt-10">
      <div class="section-title mb-4">Mitigation Strategies</div>
      <div class="suggested-fixes">
        ${mitigations.map((m, i) => `
          <div class="fix-card">
            <span class="fix-number">${i + 1}</span>
            <h4>${m.strategy_name || 'Strategy'}</h4>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0">
              ${m.implementation_complexity ? `<span class="badge badge-${m.implementation_complexity === 'low' ? 'clear' : m.implementation_complexity === 'high' ? 'critical' : 'moderate'}" style="font-size:11px">${m.implementation_complexity.toUpperCase()} COMPLEXITY</span>` : ''}
              ${m.category ? `<span class="badge" style="font-size:11px;background:var(--c-bg-elevated);color:var(--c-text-3)">${m.category}</span>` : ''}
              ${m.requires_retraining ? '<span class="badge badge-moderate" style="font-size:11px">REQUIRES RETRAINING</span>' : ''}
            </div>
            ${m.description ? `<p>${m.description}</p>` : ''}
            ${m.expected_impact ? `<div style="font-size:13px;color:var(--c-text-3);margin-top:8px">Expected impact: ${m.expected_impact}</div>` : ''}
            ${m.code_example ? `<details style="margin-top:10px"><summary style="font-size:12px;color:var(--c-accent);cursor:pointer">View Code Example</summary><pre style="margin-top:8px;padding:12px;background:var(--c-bg-elevated);border-radius:6px;font-size:11px;overflow-x:auto;white-space:pre-wrap"><code>${m.code_example}</code></pre></details>` : ''}
          </div>`).join('')}
      </div>
    </div>` : '';

  d.innerHTML = `
    <div class="verdict ${sevClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severity} BIAS DETECTED</div>
        <div class="verdict-stats">
          ${result.finding_count || validFindings.length} findings
          ${result.critical_count > 0 ? ` · <span style="color:var(--c-critical)">${result.critical_count} critical</span>` : ''}
          ${result.moderate_count > 0 ? ` · <span style="color:var(--c-moderate)">${result.moderate_count} moderate</span>` : ''}
        </div>
        <div class="verdict-meta" style="margin-top:6px">
          Model: <code class="mono" style="font-size:12px">${result.model_name || 'Unknown'}</code>
        </div>
      </div>
      <div class="verdict-actions">
        <button class="btn btn-secondary btn-sm" id="export-json-btn">Export JSON</button>
      </div>
    </div>

    ${cfHTML}
    ${scorecardHTML}
    ${findingsHTML}
    ${mitigationsHTML}

    <div class="anim-5 mt-8" style="text-align:center">
      <button class="btn btn-secondary" onclick="navigate('model-upload')">← Run Another Audit</button>
    </div>
  `;

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
