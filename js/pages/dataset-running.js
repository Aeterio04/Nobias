import { api } from '../api.js';
import { getState, setState } from '../store.js';

export function datasetRunningPage(nav) {
  const state = getState();
  const upload = state.datasetUpload;
  const config = state.datasetConfig;
  
  if (!upload || !config) {
    nav('dataset-upload');
    return document.createElement('div');
  }
  
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <h1 class="page-title">Analysing Dataset</h1>
      </div>
      <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--c-text-4)">
        <code class="mono" style="font-size:12px;background:var(--c-bg-elevated);padding:2px 8px;border-radius:4px">${upload.filename}</code>
        <span>· ${upload.row_count} rows · ${config.audit_mode} mode</span>
      </div>
    </div>
    <div class="card anim-2 mt-8">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">
        <div class="progress-pct" id="progress-pct">0%</div>
        <span style="font-size:13px;color:var(--c-text-4)" id="progress-text">Starting audit...</span>
      </div>
      <div class="progress-sub">Please wait...</div>
      <div class="progress-track"><div class="progress-fill" id="progress-bar" style="width:0%"></div></div>
    </div>
    <div id="error-display" style="display:none;margin-top:24px;padding:16px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:10px">
      <div style="font-weight:600;color:var(--c-critical);margin-bottom:8px">Audit Failed</div>
      <div id="error-message" style="color:var(--c-critical);font-size:14px"></div>
      <button class="btn btn-secondary mt-4" onclick="navigate('dataset-configure')">← Back to Configuration</button>
    </div>
  `;
  
  setTimeout(async () => {
    const progressBar = d.querySelector('#progress-bar');
    const progressPct = d.querySelector('#progress-pct');
    const progressText = d.querySelector('#progress-text');
    const errorDisplay = d.querySelector('#error-display');
    const errorMessage = d.querySelector('#error-message');
    
    let progress = 0;
    const progressInterval = setInterval(() => {
      if (progress < 90) {
        progress += Math.random() * 10;
        progressBar.style.width = `${Math.min(progress, 90)}%`;
        progressPct.textContent = `${Math.floor(Math.min(progress, 90))}%`;
      }
    }, 500);
    
    try {
      setState({ datasetLoading: true, datasetError: null });
      
      const result = await api.dataset.run({
        tmp_path: upload.tmp_path,
        protected_attributes: config.protected_attributes,
        target_column: config.target_column,
        positive_value: config.positive_value,
        audit_mode: config.audit_mode,
      });
      
      clearInterval(progressInterval);
      progressBar.style.width = '100%';
      progressPct.textContent = '100%';
      progressText.textContent = 'Complete!';
      
      setState({ datasetResult: result, datasetLoading: false });
      
      setTimeout(() => nav('dataset-results'), 500);
      
    } catch (err) {
      clearInterval(progressInterval);
      setState({ datasetLoading: false, datasetError: err.message });
      errorMessage.textContent = err.message;
      errorDisplay.style.display = 'block';
      d.querySelector('.card').style.display = 'none';
    }
  }, 100);
  
  return d;
}
