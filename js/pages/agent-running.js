// ── Agent Running — Redesigned ──
export function agentRunningPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Auditing Agent: "Hiring Assistant"</h1>
      <p style="font-size:13px;color:var(--c-text-4);margin-top:4px">Standard Mode · 28 API calls · ETA: ~3 min remaining</p>
    </div>
    <div class="card anim-2 mt-8">
      <div class="flex-between mb-2"><div class="section-label" style="margin:0">OVERALL PROGRESS</div><div class="progress-pct">78%</div></div>
      <div class="progress-track" style="height:8px"><div class="progress-fill" style="width:78%;background:var(--c-accent-teal)"></div></div>
      <div class="agent-stats"><div class="agent-stat"><strong>22 / 28</strong> API calls</div><div class="agent-stat"><strong>2m 14s</strong> elapsed</div><div class="agent-stat">ETA: <strong>~45s</strong></div></div>
    </div>
    <div class="running-grid anim-3 mt-8">
      <div class="card">
        <div class="section-label">AUDIT PHASES</div>
        <div class="phase-item"><div class="phase-icon phase-complete"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg></div><div class="phase-content"><div class="phase-name">Persona Grid Generated</div><div class="phase-desc" style="color:var(--c-clear)">10 synthetic personas · Done</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-complete"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg></div><div class="phase-content"><div class="phase-name">Explicit Attribute Testing</div><div class="phase-desc" style="color:var(--c-clear)">10 / 10 complete · Done</div></div></div>
        <div class="phase-item active-phase"><div class="phase-icon phase-running"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg></div><div class="phase-content"><div class="phase-name">Name-Based Proxy Testing</div><div class="phase-desc" style="color:var(--c-accent)">2 / 10 · Running...</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-pending"></div><div class="phase-content"><div class="phase-name" style="color:var(--c-text-5)">Context Priming Tests</div><div class="phase-desc">Pending</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-pending"></div><div class="phase-content"><div class="phase-name" style="color:var(--c-text-5)">Statistical Analysis</div><div class="phase-desc">Pending</div></div></div>
      </div>
      <div class="live-stream">
        <div class="live-stream-header"><div class="live-stream-label"><span class="live-dot"></span> LIVE RESULTS STREAM</div><button class="btn btn-secondary btn-sm">Raw Mode</button></div>
        <div class="live-stream-body">
          <div class="stream-row"><span style="color:var(--c-clear)">✓</span><span class="mono" style="color:var(--c-text-5);font-size:12px">[10:42:01]</span> <strong>Male</strong> · White · 35 → <span class="badge badge-clear" style="font-size:9px">HIRED</span></div>
          <div class="stream-row"><span style="color:var(--c-clear)">✓</span><span class="mono" style="color:var(--c-text-5);font-size:12px">[10:42:05]</span> <strong>Female</strong> · White · 35 → <span class="badge badge-clear" style="font-size:9px">HIRED</span></div>
          <div class="stream-row stream-row-warn"><span style="color:var(--c-moderate)">⚠</span><span class="mono" style="color:var(--c-text-5);font-size:12px">[10:42:12]</span> <strong>Female</strong> · Black · 35 → <span class="badge badge-critical" style="font-size:9px">REJECTED</span> <span style="color:var(--c-moderate);font-size:12px">(high variance!)</span></div>
          <div class="stream-row"><span style="color:var(--c-clear)">✓</span><span class="mono" style="color:var(--c-text-5);font-size:12px">[10:42:18]</span> <strong>Male</strong> · Black · 35 → <span class="badge badge-clear" style="font-size:9px">HIRED</span></div>
          <div class="stream-row stream-row-running"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg><span class="mono" style="color:var(--c-text-5);font-size:12px">[10:42:24]</span> Name Proxy: "Lakisha Washington" → <em style="color:var(--c-text-5)">awaiting...</em></div>
        </div>
      </div>
    </div>
    <div style="display:flex;justify-content:flex-end;margin-top:24px"><button class="btn btn-danger" onclick="navigate('agent-results')">Cancel Audit</button></div>
  `;
  return d;
}
