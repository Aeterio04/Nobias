import { getState } from '../store.js';
import { api } from '../api.js';

export function datasetResultsPage(nav) {
  const state = getState();
  const result = state.datasetResult;
  
  if (!result) {
    nav('dataset-upload');
    return document.createElement('div');
  }
  
  const severity = (result.overall_severity || 'UNKNOWN').toUpperCase();
  
  const severityClass = {
    'CRITICAL': 'verdict-critical',
    'MODERATE': 'verdict-moderate',
    'LOW': 'verdict-low',
    'CLEAR': 'verdict-clear'
  }[severity] || 'verdict-moderate';
  
  const findings = result.findings || [];
  const criticalCount = findings.filter(f => (f.severity || '').toUpperCase() === 'CRITICAL').length;
  const moderateCount = findings.filter(f => (f.severity || '').toUpperCase() === 'MODERATE').length;
  const lowCount = findings.filter(f => (f.severity || '').toUpperCase() === 'LOW').length;
  const clearCount = findings.filter(f => (f.severity || '').toUpperCase() === 'CLEAR').length;
  
  // Build label rates chart data
  const labelRates = result.label_rates || {};
  let labelRatesHTML = '';
  if (Object.keys(labelRates).length > 0) {
    const charts = Object.entries(labelRates).map(([attr, rates]) => {
      const groups = Object.entries(rates).filter(([k]) => k !== 'srd' && k !== 'dir');
      const maxRate = Math.max(...groups.map(([, v]) => v), 0.01);
      const bars = groups.map(([group, rate]) => {
        const pct = Math.round((rate / 1.0) * 100);
        const color = rate < 0.5 ? 'var(--c-critical)' : rate < 0.7 ? 'var(--c-moderate)' : 'var(--c-clear)';
        return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
          <span style="width:100px;font-size:13px;color:var(--c-text-3);text-align:right;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${group}">${group}</span>
          <div style="flex:1;background:var(--c-bg-elevated);border-radius:4px;height:24px;overflow:hidden">
            <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width 0.5s ease;display:flex;align-items:center;justify-content:flex-end;padding-right:8px">
              <span style="font-size:11px;font-weight:600;color:#fff">${(rate * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>`;
      }).join('');
      
      const srd = rates.srd != null ? `SRD: ${rates.srd}` : '';
      const dir = rates.dir != null ? `DIR: ${rates.dir}` : '';
      
      return `<div class="card" style="margin-bottom:16px">
        <div class="card-title" style="text-transform:capitalize">${attr} — Positive Outcome Rate</div>
        <div style="margin-top:12px">${bars}</div>
        ${srd || dir ? `<div style="display:flex;gap:16px;margin-top:12px;padding-top:12px;border-top:1px solid var(--c-border-row)">
          ${dir ? `<span style="font-size:12px;color:var(--c-text-4)"><code class="mono">${dir}</code></span>` : ''}
          ${srd ? `<span style="font-size:12px;color:var(--c-text-4)"><code class="mono">${srd}</code></span>` : ''}
        </div>` : ''}
      </div>`;
    }).join('');
    
    labelRatesHTML = `
    <div class="section anim-3 mt-10">
      <div class="section-title mb-4">Approval Rate by Group</div>
      ${charts}
    </div>`;
  }
  
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="verdict ${severityClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${severity} BIAS DETECTED</div>
        <div class="verdict-stats">${result.finding_count || findings.length} findings · 
          ${criticalCount > 0 ? `<span style="color:var(--c-critical)">${criticalCount} critical</span> · ` : ''}
          ${moderateCount > 0 ? `<span style="color:var(--c-moderate)">${moderateCount} moderate</span> · ` : ''}
          ${lowCount > 0 ? `<span style="color:var(--c-low)">${lowCount} low</span> · ` : ''}
          ${clearCount > 0 ? `<span style="color:var(--c-clear)">${clearCount} clear</span>` : ''}
        </div>
        <div class="verdict-meta">Dataset: ${result.dataset_name || 'Unknown'} · ${result.row_count || 0} rows analyzed</div>
      </div>
      <div class="verdict-actions">
        <button class="btn btn-secondary btn-sm" id="export-json-btn">Export JSON</button>
      </div>
    </div>
    
    <div class="section anim-2">
      <div class="section-title mb-4">Findings</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>SEVERITY</th><th>FINDING</th><th>METRIC</th><th>VALUE</th><th>THRESHOLD</th></tr></thead>
          <tbody>
            ${findings.length > 0 ? findings.map(f => {
              const fSev = (f.severity || 'LOW').toUpperCase();
              const badgeClass = `badge-${fSev.toLowerCase()}`;
              const rowClass = `row-${fSev.toLowerCase()}`;
              return `<tr class="${rowClass}">
                <td><span class="badge ${badgeClass}">${fSev}</span></td>
                <td>${f.message || f.description || f.check || '—'}</td>
                <td><code class="mono" style="font-size:12px">${f.metric || '—'}</code></td>
                <td class="mono">${f.value != null ? Number(f.value).toFixed(4) : '—'}</td>
                <td class="mono">${f.threshold != null ? Number(f.threshold).toFixed(4) : '—'}</td>
              </tr>`;
            }).join('') : '<tr><td colspan="5" style="text-align:center;color:var(--c-text-4)">No findings detected</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
    
    ${labelRatesHTML}
    
    ${result.proxy_features && result.proxy_features.length > 0 ? `
    <div class="section anim-3 mt-10">
      <div class="section-title mb-4">Proxy Features Detected</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>FEATURE</th><th>PROTECTED ATTRIBUTE</th><th>METHOD</th><th>SCORE</th></tr></thead>
          <tbody>
            ${result.proxy_features.map(p => `<tr>
              <td><code class="mono">${p.feature}</code></td>
              <td><code class="mono">${p.protected}</code></td>
              <td>${p.method}</td>
              <td class="mono" style="color:${p.score > 0.7 ? 'var(--c-critical)' : p.score > 0.5 ? 'var(--c-moderate)' : 'var(--c-text-2)'}">${Number(p.score).toFixed(4)}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </div>
    ` : ''}
    
    ${result.remediation_suggestions && result.remediation_suggestions.length > 0 ? `
    <div class="section anim-4 mt-10">
      <div class="section-title mb-4">Suggested Fixes</div>
      <div class="suggested-fixes">
        ${result.remediation_suggestions.slice(0, 3).map((r, i) => `
          <div class="fix-card">
            <span class="fix-number">${i + 1}</span>
            <h4>${r.strategy}</h4>
            <p>${r.description}</p>
            ${r.estimated_dir_after ? `<div class="fix-metric">
              <span style="color:var(--c-text-3)">Expected DIR</span>
              <span><span style="color:var(--c-moderate)">Current</span> → <span style="color:var(--c-clear)">${r.estimated_dir_after}</span></span>
            </div>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
    ` : ''}
    
    <div class="anim-5 mt-8" style="text-align:center">
      <button class="btn btn-secondary" onclick="navigate('dataset-upload')">← Run Another Audit</button>
    </div>
  `;
  
  // Wire up export button
  setTimeout(() => {
    d.querySelector('#export-json-btn')?.addEventListener('click', async () => {
      try {
        // Download the result as JSON file directly from the data we already have
        const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nobias_dataset_audit_${result.audit_id || 'export'}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        alert('Export failed: ' + err.message);
      }
    });
  }, 0);
  
  return d;
}
