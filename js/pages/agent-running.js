import { api } from '../api.js';
import { getState, setState } from '../store.js';

export function agentRunningPage(nav) {
  const state = getState();
  const config = state.agentConfig;

  if (!config) {
    nav('agent-setup');
    return document.createElement('div');
  }

  const modeLabels = { quick: '~10 API calls', standard: '~28 API calls', full: '~100 API calls' };
  const modeLabel  = modeLabels[config.audit_mode] || config.audit_mode;

  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-teal)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <h1 class="page-title">Auditing Agent</h1>
      </div>
      <p style="font-size:13px;color:var(--c-text-4)">
        ${config.audit_mode || 'standard'} mode · ${modeLabel} · this may take several minutes
      </p>
    </div>

    <div class="card anim-2 mt-8">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
        <div class="progress-pct" id="progress-pct">0%</div>
        <span style="font-size:13px;color:var(--c-text-4)" id="progress-label">Initialising audit...</span>
      </div>
      <div class="progress-track"><div class="progress-fill" id="progress-bar" style="width:0%;background:var(--c-accent-teal)"></div></div>
      <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">
        ${['Connecting to LLM','Generating personas','Running factorial tests','Name-proxy tests','Computing CFR','Generating report'].map((s, i) =>
          `<span id="step-${i}" style="font-size:12px;padding:4px 10px;border-radius:20px;background:var(--c-bg-elevated);color:var(--c-text-4)">${s}</span>`
        ).join('')}
      </div>
    </div>

    <div id="error-display" style="display:none;margin-top:24px;padding:16px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:10px">
      <div style="font-weight:600;color:var(--c-critical);margin-bottom:8px">Audit Failed</div>
      <div id="error-message" style="color:var(--c-critical);font-size:14px;font-family:var(--font-mono);white-space:pre-wrap"></div>
      <button class="btn btn-secondary mt-4" onclick="navigate('agent-setup')">← Back to Setup</button>
    </div>
  `;

  setTimeout(async () => {
    const bar    = d.querySelector('#progress-bar');
    const pct    = d.querySelector('#progress-pct');
    const label  = d.querySelector('#progress-label');
    const errDiv = d.querySelector('#error-display');
    const errMsg = d.querySelector('#error-message');

    const steps = ['Connecting to LLM','Generating personas','Running factorial tests','Name-proxy tests','Computing CFR','Generating report'];
    let progress = 0;
    let stepIdx  = 0;

    function activateStep(i) {
      if (i >= steps.length) return;
      const el = d.querySelector(`#step-${i}`);
      if (el) { el.style.background = 'var(--c-accent-teal-bg)'; el.style.color = 'var(--c-accent-teal)'; }
      label.textContent = steps[i] + '...';
    }

    activateStep(0);

    const ticker = setInterval(() => {
      if (progress < 88) {
        progress = Math.min(progress + 0.8, 88);
        bar.style.width = `${progress}%`;
        pct.textContent = `${Math.floor(progress)}%`;
        const expected = Math.floor((progress / 88) * steps.length);
        if (expected > stepIdx && expected < steps.length) {
          stepIdx = expected;
          activateStep(stepIdx);
        }
      }
    }, 400);

    try {
      setState({ agentLoading: true, agentError: null });

      const result = await api.agent.run(config);

      clearInterval(ticker);
      steps.forEach((_, i) => {
        const el = d.querySelector(`#step-${i}`);
        if (el) { el.style.background = 'var(--c-clear-bg)'; el.style.color = 'var(--c-clear)'; }
      });
      bar.style.width = '100%';
      pct.textContent = '100%';
      label.textContent = 'Complete!';

      setState({ agentResult: result, agentLoading: false });
      setTimeout(() => nav('agent-results'), 600);

    } catch (err) {
      clearInterval(ticker);
      setState({ agentLoading: false, agentError: err.message });
      errMsg.textContent = err.message;
      errDiv.style.display = 'block';
      d.querySelector('.card').style.display = 'none';
    }
  }, 100);

  return d;
}
