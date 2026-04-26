// ── Audit Comparison — Redesigned ──
export function auditComparisonPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1"><div class="flex-between mb-8"><h1 class="page-title">Audit Comparison</h1><button class="btn btn-secondary">Export Comparison Report</button></div></div>
    <div class="comparison-cards anim-2">
      <div class="comparison-card" style="border-left:4px solid var(--c-moderate)"><div class="flex-between"><h3>Before — Audit #a1b2c3</h3><span class="badge badge-moderate">MODERATE</span></div><div class="meta">Apr 23, 2026 · 9:14 PM</div></div>
      <div class="comparison-arrow">→</div>
      <div class="comparison-card" style="border-left:4px solid var(--c-low)"><div class="flex-between"><h3>After — Audit #d4e5f6</h3><span class="badge badge-low">LOW</span></div><div class="meta">Apr 23, 2026 · 9:22 PM</div></div>
    </div>
    <div class="improvement-banner anim-3">
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--c-clear)" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg><strong style="color:var(--c-clear);font-size:16px">Significant Improvement</strong></div>
        <div style="font-size:13px;color:var(--c-text-4);margin-bottom:8px">Overall CFR</div>
        <div class="improvement-values"><span class="improvement-old">11.2%</span><span style="color:var(--c-clear);font-size:18px">→</span><span class="improvement-new">3.8%</span><span class="improvement-change">(↓ 66% reduction)</span></div>
      </div>
      <div><span class="badge badge-clear" style="font-size:12px">MODERATE → LOW</span></div>
    </div>
    <div class="anim-4">
      <div class="table-container">
        <table class="table">
          <thead><tr><th>FINDING</th><th style="color:var(--c-moderate)">BEFORE</th><th style="color:var(--c-clear)">AFTER</th><th>CHANGE</th><th>STATUS</th></tr></thead>
          <tbody>
            <tr><td style="font-weight:500;color:var(--c-text-1)">Gender CFR</td><td class="mono">12.6%</td><td class="mono">2.1%</td><td style="color:var(--c-clear);font-weight:600">↓ 83%</td><td><span class="badge badge-clear">FIXED</span></td></tr>
            <tr><td style="font-weight:500;color:var(--c-text-1)">Race (name-based)</td><td class="mono">9.1%</td><td class="mono">4.8%</td><td style="color:var(--c-clear);font-weight:600">↓ 47%</td><td><span class="badge badge-moderate">IMPROVED</span></td></tr>
            <tr><td style="font-weight:500;color:var(--c-text-1)">Context Prime CFR</td><td class="mono">14.2%</td><td class="mono">5.1%</td><td style="color:var(--c-clear);font-weight:600">↓ 64%</td><td><span class="badge badge-moderate">IMPROVED</span></td></tr>
            <tr><td style="font-weight:500;color:var(--c-text-1)">Age CFR</td><td class="mono">1.3%</td><td class="mono">1.1%</td><td style="color:var(--c-clear);font-weight:600">↓ 15%</td><td><span class="badge badge-clear">STILL CLEAR</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
  return d;
}
