import { getState } from '../store.js';

export function agentResultsPage(nav) {
  const d = document.createElement('div');
  const result = getState().agentResult;

  if (!result) {
    d.innerHTML = `
      <div style="padding:60px;text-align:center">
        <p style="font-size:16px;color:var(--c-text-4);margin-bottom:20px">
          No audit results found. Please run an audit first.
        </p>
        <button class="btn btn-secondary" onclick="navigate('agent-setup')">← Go to Agent Auditor</button>
      </div>`;
    return d;
  }

  const severity  = (result.overall_severity || 'UNKNOWN').toUpperCase();
  const sevClass  = { CRITICAL:'verdict-critical', MODERATE:'verdict-moderate', LOW:'verdict-low', CLEAR:'verdict-clear' }[severity] || 'verdict-moderate';
  const cfrPct    = result.overall_cfr_pct || `${((result.overall_cfr || 0) * 100).toFixed(1)}%`;

  // ── CFR by attribute ─────────────────────────────────────────────────────
  const cfrByAttr = result.cfr_by_attribute || {};
  const hasCFR    = Object.keys(cfrByAttr).length > 0;
  const cfrHTML   = hasCFR ? `
    <div class="section anim-2 mt-8">
      <div class="section-title mb-4">CFR by Attribute</div>
      <div class="card">
        ${Object.entries(cfrByAttr).map(([attr, val]) => {
          const pct   = Math.min(val * 100, 100);
          const color = val > 0.13 ? 'var(--c-critical)' : val > 0.05 ? 'var(--c-moderate)' : 'var(--c-clear)';
          const label = result.cfr_by_attribute_pct?.[attr] || `${(val * 100).toFixed(1)}%`;
          return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
            <span style="width:80px;font-size:13px;color:var(--c-text-3);text-align:right;text-transform:capitalize;flex-shrink:0">${attr}</span>
            <div style="flex:1;background:var(--c-bg-elevated);border-radius:4px;height:28px;overflow:hidden">
              <div style="width:${Math.max(pct, 3)}%;height:100%;background:${color};border-radius:4px;display:flex;align-items:center;padding-left:10px;transition:width 0.5s">
                <span style="font-size:12px;font-weight:600;color:#fff">${label}</span>
              </div>
            </div>
          </div>`;
        }).join('')}
        <div style="display:flex;gap:16px;margin-top:12px;padding-top:12px;border-top:1px solid var(--c-border-row);font-size:11px;color:var(--c-text-5)">
          <span>◼ <span style="color:var(--c-clear)">< 5% Best-in-class</span></span>
          <span>◼ <span style="color:var(--c-moderate)">5–13% Needs improvement</span></span>
          <span>◼ <span style="color:var(--c-critical)">> 13% Critical</span></span>
        </div>
      </div>
    </div>` : '';

  // ── EEOC AIR ─────────────────────────────────────────────────────────────
  const eeocAir  = result.eeoc_air || {};
  const hasEEOC  = Object.keys(eeocAir).length > 0;
  const eeocHTML = hasEEOC ? `
    <div class="section anim-2 mt-8">
      <div class="section-title mb-4">EEOC Adverse Impact Ratio</div>
      <div class="card">
        ${Object.entries(eeocAir).map(([attr, data]) => {
          const isViolation = (data.status || '').toUpperCase() === 'VIOLATION';
          return `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--c-border-row)">
            <span style="font-size:14px;color:var(--c-text-2);text-transform:capitalize">${attr}</span>
            <div style="display:flex;align-items:center;gap:12px">
              <span class="mono" style="font-size:13px;color:var(--c-text-3)">AIR: ${data.air ?? '—'}</span>
              <span class="badge badge-${isViolation ? 'critical' : 'clear'}">${data.status || '—'}</span>
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>` : '';

  // ── Findings ──────────────────────────────────────────────────────────────
  const findings    = result.findings || [];
  const findingsHTML = `
    <div class="section anim-3 mt-8">
      <div class="section-title mb-4">Audit Findings</div>
      ${findings.length > 0 ? `
      <div class="table-container">
        <table class="table">
          <thead><tr><th>SEVERITY</th><th>FINDING</th><th>ATTRIBUTE</th><th>TEST TYPE</th><th>CFR</th></tr></thead>
          <tbody>
            ${findings.map(f => {
              const sev = (f.severity || 'LOW').toUpperCase();
              return `<tr class="row-${sev.toLowerCase()}">
                <td><span class="badge badge-${sev.toLowerCase()}">${sev}</span></td>
                <td style="font-size:13px">${f.description || '—'}</td>
                <td><code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 6px;border-radius:3px">${f.attribute || '—'}</code></td>
                <td style="font-size:12px;color:var(--c-text-3)">${f.test_type || '—'}</td>
                <td class="mono" style="color:var(--c-${sev.toLowerCase()})">${f.cfr_pct || (f.cfr != null ? (f.cfr * 100).toFixed(1) + '%' : '—')}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>` : '<div style="padding:24px;text-align:center;color:var(--c-text-4)">No significant bias detected.</div>'}
    </div>`;

  // ── Persona results ───────────────────────────────────────────────────────
  const personas    = result.persona_results || [];
  const personasHTML = personas.length > 0 ? `
    <div class="section anim-4 mt-10">
      <div class="section-title mb-4">Persona Results <span style="font-size:13px;font-weight:400;color:var(--c-text-4)">(${personas.length} tested)</span></div>
      <div class="table-container" style="max-height:400px;overflow-y:auto">
        <table class="table">
          <thead><tr><th>ID</th><th>ATTRIBUTES</th><th>DECISION</th><th>SCORE</th></tr></thead>
          <tbody>
            ${personas.map(p => {
              const attrStr   = Object.entries(p.attributes || {}).map(([k, v]) => `${k}: ${v}`).join(', ');
              const isNeg     = ['reject','rejected','negative','denied'].some(w => (p.decision || '').toLowerCase().includes(w));
              return `<tr>
                <td class="mono" style="font-size:12px">${p.persona_id || '—'}</td>
                <td style="font-size:13px">${attrStr || '—'}</td>
                <td><span class="badge badge-${isNeg ? 'critical' : 'clear'}">${p.decision || '—'}</span></td>
                <td class="mono">${p.score != null ? Number(p.score).toFixed(4) : '—'}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>` : '';

  // ── Prompt suggestions ────────────────────────────────────────────────────
  const suggestions    = result.prompt_suggestions || [];
  const suggestionsHTML = suggestions.length > 0 ? `
    <div class="section anim-5 mt-10">
      <div class="section-title mb-4">Prompt Optimization Suggestions</div>
      ${suggestions.map((s, i) => `
        <div class="card" style="margin-bottom:16px">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div class="card-title" style="margin:0">Suggestion ${i + 1}</div>
            <button class="btn btn-secondary btn-sm copy-suggestion" data-idx="${i}">Copy Suggested Prompt</button>
          </div>
          ${s.original_segment || s.suggested_change ? `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px">
            ${s.original_segment ? `<div>
              <div style="font-size:11px;color:var(--c-text-5);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Original</div>
              <div style="padding:12px;background:var(--c-critical-bg);border-radius:6px;font-size:13px;font-family:var(--font-mono);border:1px solid var(--c-critical-bdr)">${s.original_segment}</div>
            </div>` : ''}
            ${s.suggested_change ? `<div>
              <div style="font-size:11px;color:var(--c-text-5);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Suggested</div>
              <div style="padding:12px;background:var(--c-clear-bg);border-radius:6px;font-size:13px;font-family:var(--font-mono);border:1px solid var(--c-clear-bdr)" id="suggestion-text-${i}">${s.suggested_change}</div>
            </div>` : ''}
          </div>` : ''}
          ${s.rationale ? `<div style="font-size:13px;color:var(--c-text-3)"><strong>Rationale:</strong> ${s.rationale}</div>` : ''}
        </div>`).join('')}
    </div>` : '';

  d.innerHTML = `
    <div class="verdict ${sevClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severity} BIAS DETECTED</div>
        <div style="font-size:32px;font-weight:700;letter-spacing:-0.03em;color:var(--c-text-1);margin:8px 0">
          Overall CFR: ${cfrPct}
        </div>
        <div class="verdict-stats">
          ${result.finding_count || findings.length} findings
          ${result.critical_count > 0 ? ` · <span style="color:var(--c-critical)">${result.critical_count} critical</span>` : ''}
          ${result.persona_count  > 0 ? ` · ${result.persona_count} personas tested` : ''}
        </div>
      </div>
      <div style="flex-shrink:0">
        <button class="btn btn-secondary btn-sm" id="export-json-btn">Export JSON</button>
      </div>
    </div>

    ${cfrHTML}
    ${eeocHTML}
    ${findingsHTML}
    ${personasHTML}
    ${suggestionsHTML}

    <div class="anim-5 mt-8" style="text-align:center">
      <button class="btn btn-secondary" onclick="navigate('agent-setup')">← Run Another Audit</button>
    </div>
  `;

  setTimeout(() => {
    d.querySelector('#export-json-btn')?.addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url;
      a.download = `nobias_agent_audit_${result.audit_id || 'export'}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });

    d.querySelectorAll('.copy-suggestion').forEach(btn => {
      btn.addEventListener('click', () => {
        const text = d.querySelector(`#suggestion-text-${btn.dataset.idx}`)?.textContent || '';
        navigator.clipboard.writeText(text).then(() => {
          btn.textContent = 'Copied!';
          setTimeout(() => btn.textContent = 'Copy Suggested Prompt', 2000);
        }).catch(() => {
          btn.textContent = 'Copy failed';
          setTimeout(() => btn.textContent = 'Copy Suggested Prompt', 2000);
        });
      });
    });
  }, 0);

  return d;
}
