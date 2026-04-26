// ── Dataset Results — Redesigned ──
export function datasetResultsPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="verdict verdict-moderate anim-1">
      <div style="flex:1">
        <div class="verdict-title">MODERATE BIAS DETECTED</div>
        <div class="verdict-stats">3 findings · <span style="color:var(--c-critical)">1 critical</span> · <span style="color:var(--c-moderate)">1 moderate</span> · <span style="color:var(--c-low)">1 low</span></div>
        <div class="verdict-meta">Dataset: hiring_data.csv · 12,847 rows analyzed · Completed Apr 25, 2026</div>
      </div>
      <div class="verdict-actions">
        <button class="btn btn-secondary btn-sm">Export PDF</button>
        <button class="btn btn-secondary btn-sm">Export JSON</button>
        <button class="btn btn-primary btn-sm">View Remediation</button>
      </div>
    </div>
    <div class="section anim-2">
      <div class="section-title mb-4">Findings</div>
      <div class="table-container">
        <table class="table">
          <thead><tr><th>SEVERITY</th><th>FINDING</th><th>ATTRIBUTE</th><th>METRIC</th><th>VALUE</th><th>ACTION</th></tr></thead>
          <tbody>
            <tr class="row-critical"><td><span class="badge badge-critical">CRITICAL</span></td><td>Female applicants approved at 52% vs 78% for males</td><td><code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 6px;border-radius:3px">gender</code></td><td>Disparate Impact Ratio</td><td class="mono" style="color:var(--c-critical)">0.67</td><td><a href="#" class="btn-ghost">Details ↗</a></td></tr>
            <tr class="row-moderate"><td><span class="badge badge-moderate">MODERATE</span></td><td>ZIP code strongly correlates with race (r=0.74)</td><td><code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 6px;border-radius:3px">race</code></td><td>Correlation</td><td class="mono" style="color:var(--c-moderate)">0.74</td><td><a href="#" class="btn-ghost">Details ↗</a></td></tr>
            <tr class="row-low"><td><span class="badge badge-low">LOW</span></td><td>Age group 60+ has 3% fewer positive labels</td><td><code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 6px;border-radius:3px">age</code></td><td>Label Bias</td><td class="mono" style="color:var(--c-low)">0.03</td><td><a href="#" class="btn-ghost">Details ↗</a></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="results-charts anim-3 mt-10">
      <div class="chart-container"><div class="chart-title">Approval Rate by Group</div><div class="chart-canvas" id="chart-approval"></div></div>
      <div class="chart-container"><div class="chart-title">Group Representation</div><div class="chart-canvas" id="chart-representation"></div></div>
    </div>
    <div class="results-charts anim-4">
      <div class="chart-container"><div class="chart-title">Missing Data Heatmap</div><div class="chart-canvas" id="chart-heatmap"></div></div>
      <div class="chart-container"><div class="chart-title">Feature Correlation Matrix</div><div class="chart-canvas" id="chart-correlation"></div></div>
    </div>
    <div class="section anim-5 mt-10">
      <div class="section-title mb-4">Suggested Fixes</div>
      <div class="suggested-fixes">
        <div class="fix-card"><span class="fix-number">1</span><h4>Reweight Samples</h4><p>Balance gender representation in training data.</p><div class="fix-metric"><span style="color:var(--c-text-3)">M/F Ratio</span><span><span style="color:var(--c-critical)">72/28</span> → <span style="color:var(--c-clear)">50/50</span></span></div><button class="btn btn-secondary btn-full btn-sm" style="margin-top:12px">Apply & Download</button></div>
        <div class="fix-card"><span class="fix-number">2</span><h4>Drop Feature 'ZIP Code'</h4><p>Remove highly correlated proxy variable.</p><div class="fix-metric"><span style="color:var(--c-text-3)">Proxy Risk</span><span><span style="color:var(--c-critical)">High</span> → <span style="color:var(--c-clear)">None</span></span></div><button class="btn btn-secondary btn-full btn-sm" style="margin-top:12px">Apply & Download</button></div>
        <div class="fix-card"><span class="fix-number">3</span><h4>Generate Synthetic Data</h4><p>Augment underrepresented age groups.</p><div class="fix-metric"><span style="color:var(--c-text-3)">60+ Group</span><span><span style="color:var(--c-moderate)">8%</span> → <span style="color:var(--c-clear)">15%</span></span></div><button class="btn btn-secondary btn-full btn-sm" style="margin-top:12px;opacity:0.5" disabled>Coming Soon</button></div>
      </div>
    </div>
  `;
  setTimeout(() => renderCharts(), 50);
  return d;
}
function renderCharts() {
  const a = document.getElementById('chart-approval');
  if (a) a.innerHTML = `<div style="display:flex;align-items:flex-end;justify-content:center;gap:32px;height:180px;padding:0 20px">
    ${[['Male / Female',78,52],['Race',72,58],['Age',68,65]].map(([l,h1,h2])=>`<div style="text-align:center"><div style="height:140px;display:flex;align-items:flex-end;justify-content:center;gap:4px"><div style="width:24px;height:${h1}%;background:var(--c-accent);border-radius:4px 4px 0 0"></div><div style="width:24px;height:${h2}%;background:#A5B4FC;border-radius:4px 4px 0 0"></div></div><div style="font-size:12px;color:var(--c-text-4);margin-top:8px">${l}</div></div>`).join('')}
  </div>`;
  const r = document.getElementById('chart-representation');
  if (r) r.innerHTML = `<div style="display:flex;justify-content:space-around;align-items:center;height:180px">
    ${['Gender','Race','Age'].map((l,i)=>{const p=[72,45,60][i];return`<div style="text-align:center"><div style="width:80px;height:80px;border-radius:50%;background:conic-gradient(var(--c-accent) 0% ${p}%,#E8E6E1 ${p}% 100%);display:flex;align-items:center;justify-content:center;margin:0 auto"><div style="width:50px;height:50px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;color:var(--c-text-1)">${l}</div></div></div>`;}).join('')}
  </div>`;
  const h = document.getElementById('chart-heatmap');
  if (h) {const rows=[['Age',0.02,0.15,0.05],['Gender',0.08,0.03,0.12],['Income',0.04,0.18,0.07]],cols=['Age','Gender','Income'];h.innerHTML=`<div style="display:grid;grid-template-columns:60px repeat(3,1fr);gap:2px;padding:20px"><div></div>${cols.map(c=>`<div style="text-align:center;font-size:12px;color:var(--c-text-4)">${c}</div>`).join('')}${rows.map(r=>`<div style="font-size:12px;color:var(--c-text-4);display:flex;align-items:center">${r[0]}</div>${[1,2,3].map(i=>{const v=r[i],int=Math.min(v*5,1);return`<div style="background:rgba(91,91,214,${int});border-radius:4px;padding:12px;text-align:center;font-family:var(--font-mono);font-size:12px;color:${int>0.4?'#fff':'var(--c-text-1)'}">${v.toFixed(2)}</div>`}).join('')}`).join('')}</div>`;}
  const c = document.getElementById('chart-correlation');
  if (c) {const data=[['ZIP',1.0,0.52,0.74],['Edu',0.52,1.0,0.31],['Race',0.74,0.31,1.0]],labels=['ZIP','Edu','Race'];c.innerHTML=`<div style="display:grid;grid-template-columns:50px repeat(3,1fr);gap:2px;padding:20px"><div></div>${labels.map(l=>`<div style="text-align:center;font-size:12px;color:var(--c-text-4)">${l}</div>`).join('')}${data.map(r=>`<div style="font-size:12px;color:var(--c-text-4);display:flex;align-items:center">${r[0]}</div>${[1,2,3].map(i=>{const v=r[i],color=v>0.7?'var(--c-critical)':v>0.5?'var(--c-moderate)':'var(--c-accent)',bg=v>0.7?'var(--c-critical-bg)':v>0.5?'var(--c-moderate-bg)':'rgba(91,91,214,0.1)';return`<div style="background:${bg};border-radius:4px;padding:12px;text-align:center;font-family:var(--font-mono);font-size:12px;color:${color};font-weight:${v>0.5?'600':'400'}">${v.toFixed(2)}</div>`}).join('')}`).join('')}</div>`;}
}
