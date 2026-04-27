import { api } from '../api.js';
import { getState, setState } from '../store.js';

export function modelRunningPage(nav) {
  const state = getState();
  const config = state.modelConfig;

  if (!config) {
    nav('model-upload');
    return document.createElement('div');
  }

  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-violet)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <h1 class="page-title">Auditing Model</h1>
      </div>
      <p style="font-size:13px;color:var(--c-text-4)">
        Running fairness analysis · this may take 10–30 seconds
      </p>
    </div>

    <div class="card anim-2 mt-8">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
        <div class="progress-pct" id="progress-pct">0%</div>
        <span style="font-size:13px;color:var(--c-text-4)" id="progress-label">Starting audit...</span>
      </div>
      <div class="progress-track"><div class="progress-fill" id="progress-bar" style="width:0%"></div></div>
      <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px" id="step-list">
        ${['Loading model & data','Computing baseline metrics','Counterfactual flip tests','Fairness metrics','Intersectional analysis','Generating findings'].map((s,i) =>
          `<span id="step-${i}" style="font-size:12px;padding:4px 10px;border-radius:20px;background:var(--c-bg-elevated);color:var(--c-text-4)">${s}</span>`
        ).join('')}
      </div>
    </div>

    <div id="error-display" style="display:none;margin-top:24px;padding:16px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:10px">
      <div style="font-weight:600;color:var(--c-critical);margin-bottom:8px">Audit Failed</div>
      <div id="error-message" style="color:var(--c-critical);font-size:14px;font-family:var(--font-mono);white-space:pre-wrap"></div>
      <button class="btn btn-secondary mt-4" onclick="navigate('model-upload')">← Back to Upload</button>
    </div>
  `;

  setTimeout(async () => {
    const bar      = d.querySelector('#progress-bar');
    const pct      = d.querySelector('#progress-pct');
    const label    = d.querySelector('#progress-label');
    const errDiv   = d.querySelector('#error-display');
    const errMsg   = d.querySelector('#error-message');

    const steps = [
      'Loading model & data',
      'Computing baseline metrics',
      'Counterfactual flip tests',
      'Fairness metrics',
      'Intersectional analysis',
      'Generating findings',
    ];

    let currentStep = 0;
    const stepMs = [800, 1200, 2000, 1500, 1000, 800];

    function activateStep(i) {
      if (i >= steps.length) return;
      const el = d.querySelector(`#step-${i}`);
      if (el) {
        el.style.background = 'var(--c-accent-violet-bg)';
        el.style.color = 'var(--c-accent-violet)';
      }
      label.textContent = steps[i] + '...';
    }

    // Animate progress up to 88% while waiting for the API
    let progress = 0;
    activateStep(0);

    const ticker = setInterval(() => {
      if (progress < 88) {
        const increment = currentStep < steps.length
          ? (88 / steps.length) / (stepMs[currentStep] / 300)
          : 1;
        progress = Math.min(progress + increment, 88);
        bar.style.width = `${progress}%`;
        pct.textContent = `${Math.floor(progress)}%`;

        // Advance step markers
        const expectedStep = Math.floor((progress / 88) * steps.length);
        if (expectedStep > currentStep && expectedStep < steps.length) {
          currentStep = expectedStep;
          activateStep(currentStep);
        }
      }
    }, 300);

    try {
      setState({ modelLoading: true, modelError: null });

      const result = await api.model.run({
        model_path:           config.model_path,
        testdata_path:        config.testdata_path,
        protected_attributes: config.protected_attributes,
        target_column:        config.target_column,
        positive_value:       config.positive_value,
      });

      clearInterval(ticker);

      // Complete all steps
      steps.forEach((_, i) => {
        const el = d.querySelector(`#step-${i}`);
        if (el) { el.style.background = 'var(--c-clear-bg)'; el.style.color = 'var(--c-clear)'; }
      });
      bar.style.width = '100%';
      pct.textContent = '100%';
      label.textContent = 'Complete!';

      setState({ modelResult: result, modelLoading: false });
      setTimeout(() => nav('model-results'), 600);

    } catch (err) {
      clearInterval(ticker);
      setState({ modelLoading: false, modelError: err.message });
      errMsg.textContent = err.message;
      errDiv.style.display = 'block';
      d.querySelector('.card').style.display = 'none';
    }
  }, 100);

  return d;
}
