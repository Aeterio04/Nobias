import { getState } from '../store.js';

export function datasetResultsPage(nav) {
  const state = getState();
  const result = state.datasetResult;
  
  if (!result) {
    nav('dataset-upload');
    return document.createElement('div');
  }
  
  const severityClass = {
    'CRITICAL': 'verdict-critical',
    'MODERATE': 'verdict-moderate',
    'LOW': 'verdict-low',
    'CLEAR': 'verdict-clear'
  }[result.overall_severity] || 'verdict-moderate';
  
  const severityBadge = {
    'CRITICAL': 'badge-critical',
    'MODERATE': 'badge-moderate',
    'LOW': 'badge-low',
    'CLEAR': 'badge-clear'
  }[result.overall_severity] || 'badge-moderate';
  
  const criticalCount = result.findings.filter(f => f.severity === 'CRITICAL').length;
  const moderateCount = result.findings.filter(f => f.severity === 'MODERATE').length;
  const lowCount = result.findings.filter(f => f.severity === 'LOW').length;
  
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="verdict ${severityClass} anim-1">
      <div style="flex:1">
        <div class="verdict-title">${result.overall_severity} BIAS DETECTED</div>
        <div class="verdict-stats">${result.finding_count} findings · 
          ${criticalCount > 0 ? `<span style="color:var(--c-critical)">${criticalCount} critical</span> · ` : ''}
          ${moderateCount > 0 ? `<span style="color:var(--c-moderate)">${moderateCount} moderate</span> · ` : ''}
          ${lowCount > 0 ? `<span style="color:var(--c-low)">${lowCount} low</span>` : ''}
        </div>
        <div class="verdict-meta">Dataset: ${result.dataset_name} · ${result.row_count} rows analyzed</div>
      </div>
      <div class="verdict-actions">
        <button class="btn btn-secondary btn-sm" onclick="alert('Export feature coming soon')">Export PDF</button>
        <button class="btn btn-secondary btn-sm" onclick="alert('Export feature coming soon')">Export JSON</button>
      </div>
    </div>
    
    <div class="section anim-2">
      <div class="section-title mb-4">Findings</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>SEVERITY</th><th>FINDING</th><th>METRIC</th><th>VALUE</th><th>THRESHOLD</th></tr></thead>
          <tbody>
            ${result.findings.map(f => {
              const rowClass = `row-${f.severity.toLowerCase()}`;
              const badgeClass = `badge-${f.severity.toLowerCase()}`;
              return `<tr class="${rowClass}">
                <td><span class="badge ${badgeClass}">${f.severity}</span></td>
                <td>${f.message}</td>
                <td><code class="mono" style="font-size:12px">${f.metric}</code></td>
                <td class="mono">${f.value}</td>
                <td class="mono">${f.threshold}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
    
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
              <td class="mono" style="color:${p.score > 0.7 ? 'var(--c-critical)' : p.score > 0.5 ? 'var(--c-moderate)' : 'var(--c-text-2)'}">${p.score}</td>
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
            <button class="btn btn-secondary btn-full btn-sm" style="margin-top:12px" onclick="alert('Remediation download coming soon')">Apply & Download</button>
          </div>
        `).join('')}
      </div>
    </div>
    ` : ''}
    
    <div class="anim-5 mt-8" style="text-align:center">
      <button class="btn btn-secondary" onclick="navigate('dataset-upload')">← Run Another Audit</button>
    </div>
  `;
  
  return d;
}
