// ── Dataset Running — Redesigned ──
export function datasetRunningPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <h1 class="page-title">Analysing Dataset</h1>
      </div>
      <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--c-text-4)">
        <code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 8px;border-radius:4px;border:1px solid var(--c-border-soft)">hiring_data.csv</code>
        <span>· 12,847 rows · Standard mode</span>
      </div>
    </div>
    <div class="card anim-2 mt-8">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">
        <div class="progress-pct">67%</div>
        <span style="font-size:13px;color:var(--c-text-4)">22 / 32 checks complete</span>
      </div>
      <div class="progress-sub">ETA ~45 seconds</div>
      <div class="progress-track"><div class="progress-fill" style="width:67%"></div></div>
    </div>
    <div class="running-grid anim-3 mt-8">
      <div class="card">
        <div class="section-label">AUDIT EXECUTION PLAN</div>
        <div class="phase-item"><div class="phase-icon phase-complete"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg></div><div class="phase-content"><div class="phase-name">Representation Analysis</div><div class="phase-desc">Checking group distribution across protected attributes</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-complete"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg></div><div class="phase-content"><div class="phase-name">Missing Data Patterns</div><div class="phase-desc">Detecting if missingness correlates with demographics</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-complete"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg></div><div class="phase-content"><div class="phase-name">Feature-Attribute Correlation</div><div class="phase-desc">Finding proxy variables for protected attributes</div></div></div>
        <div class="phase-item active-phase"><div class="phase-icon phase-running"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg></div><div class="phase-content"><div class="phase-name">Label Bias Scan <span class="badge badge-accent" style="font-size:9px;margin-left:6px">RUNNING</span></div><div class="phase-desc">Testing if outcome rates differ across demographic groups</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-pending"></div><div class="phase-content"><div class="phase-name" style="color:var(--c-text-4)">Intersectional Analysis</div><div class="phase-desc">Testing combinations of multiple attributes</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-pending"></div><div class="phase-content"><div class="phase-name" style="color:var(--c-text-4)">Disparate Impact Calculation</div><div class="phase-desc">Computing legal fairness metrics</div></div></div>
        <div class="phase-item"><div class="phase-icon phase-pending"></div><div class="phase-content"><div class="phase-name" style="color:var(--c-text-4)">Remediation Planning</div><div class="phase-desc">Generating suggested fixes</div></div></div>
      </div>
      <div class="terminal">
        <div class="terminal-header">
          <div class="terminal-dots"><span></span><span></span><span></span></div>
          <div class="terminal-label">LIVE AUDIT LOGS</div>
        </div>
        <div class="terminal-body">
          <div class="log-line">Initializing Dataset Auditor engine v2.4.1...</div>
          <div class="log-line">Loading standard rule configurations... <span class="log-success">DONE</span></div>
          <div class="log-line"><span class="log-ts">[12:34:01]</span> Representation: gender=Male 72.1%, Female 27.9%</div>
          <div class="log-line" style="color:#FFD60A"><span class="log-ts">[12:34:01]</span> WARN: High class imbalance detected in 'gender'</div>
          <div class="log-line"><span class="log-ts">[12:34:02]</span> Scanning for missing data patterns... <span class="log-success">OK</span></div>
          <div class="log-line"><span class="log-ts">[12:34:03]</span> Detected label skew: Male <span class="log-value">78.2%</span>, Female <span class="log-value">52.1%</span></div>
          <div class="log-line"><span class="log-ts">[12:34:04]</span> Calculating p-values for outcome disparity...</div>
          <div class="log-line"><span class="log-ts">[12:34:05]</span> Running disparate impact for column: gender...</div>
          <div class="log-line"><span style="color:#fff">></span> <span class="log-cursor">▋</span></div>
        </div>
      </div>
    </div>
    <div class="anim-4 mt-6" style="text-align:center">
      <p style="font-size:13px;color:var(--c-text-5)">Results will appear automatically when the audit completes.</p>
    </div>
    <div style="display:flex;justify-content:flex-end;margin-top:24px">
      <button class="btn btn-danger" onclick="navigate('dataset-results')">Cancel Audit</button>
    </div>
  `;
  return d;
}
