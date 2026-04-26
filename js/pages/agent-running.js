// ── Agent Running — Redesigned ──
import { getState } from '../store.js';

export function agentRunningPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Auditing Agent: "Hiring Assistant"</h1>
      <p style="font-size:13px;color:var(--c-text-4);margin-top:4px">Standard Mode · ${state.agentProgress || 0}% complete</p>
    </div>
    <div class="card anim-2 mt-8">
      <div class="flex-between mb-2"><div class="section-label" style="margin:0">OVERALL PROGRESS</div><div class="progress-pct">${state.agentProgress || 0}%</div></div>
      <div class="progress-track" style="height:8px"><div class="progress-fill" style="width:${state.agentProgress || 0}%;background:var(--c-accent-teal)"></div></div>
      <div class="agent-stats"><div class="agent-stat">Running audit...</div></div>
    </div>
    <div class="running-grid anim-3 mt-8">
      <div class="card">
        <div class="section-label">AUDIT PHASES</div>
        <div class="phase-item active-phase"><div class="phase-icon phase-running"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg></div><div class="phase-content"><div class="phase-name">Running Audit</div><div class="phase-desc" style="color:var(--c-accent)">Please wait...</div></div></div>
      </div>
      <div class="live-stream">
        <div class="live-stream-header"><div class="live-stream-label"><span class="live-dot"></span> LIVE RESULTS STREAM</div></div>
        <div class="live-stream-body">
          <div class="stream-row stream-row-running"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg><span class="mono" style="color:var(--c-text-5);font-size:12px">Processing...</span></div>
        </div>
      </div>
    </div>
    ${state.agentError ? `<div class="compat-banner compat-error anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg><span>${state.agentError}</span></div>` : ''}
  `;
  
  if (state.agentResult) {
    setTimeout(() => nav('agent-results'), 500);
  }
  
  return d;
}
