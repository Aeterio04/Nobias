// ── Model Upload — Redesigned ──
export function modelUploadPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1"><h1 class="page-title">Model Auditor</h1><p class="page-subtitle">Upload your trained model and test dataset to audit for fairness.</p></div>
    <div class="card anim-2 mt-6">
      <div class="model-upload-grid">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600">1</span>
            <span style="font-size:16px;font-weight:600;color:var(--c-text-1)">Your Trained Model</span>
          </div>
          <div class="dropzone" style="padding:40px 24px">
            <div class="dropzone-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
            <div class="dropzone-title" style="font-size:14px">Drop your model file here</div>
            <div class="dropzone-sub">or <a href="#" class="dropzone-link" onclick="event.preventDefault()">click to browse</a></div>
            <div class="dropzone-formats" style="margin-top:8px"><span class="format-badge">.PKL</span><span class="format-badge">.JOBLIB</span><span class="format-badge">.ONNX</span><span class="format-badge">.H5</span></div>
          </div>
        </div>
        <div class="model-plus">+</div>
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600">2</span>
            <span style="font-size:16px;font-weight:600;color:var(--c-text-1)">Test Dataset (CSV)</span>
          </div>
          <div class="dropzone" style="padding:40px 24px">
            <div class="dropzone-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
            <div class="dropzone-title" style="font-size:14px">Drop your test CSV here</div>
            <div class="dropzone-sub">Same features as your model + ground truth labels</div>
            <div class="dropzone-formats" style="margin-top:8px"><span class="format-badge">.CSV</span><span class="format-badge">.XLSX</span></div>
          </div>
        </div>
      </div>
    </div>
    <div class="compat-banner compat-success anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg><span>Feature compatibility: <strong>14/14 features match</strong></span></div>
    <div class="divider-text anim-3">or try a sample model + dataset pair</div>
    <div class="model-samples anim-4">
      <div class="sample-card" style="display:flex;align-items:center;gap:16px"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-violet)" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg><div><div class="sample-card-title">COMPAS Recidivism Classifier</div><div class="sample-card-desc">Pre-loaded random forest model and ProPublica dataset.</div></div></div>
      <div class="sample-card" style="display:flex;align-items:center;gap:16px"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-violet)" stroke-width="1.5"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg><div><div class="sample-card-title">Credit Scoring Model</div><div class="sample-card-desc">Gradient boosting classifier for loan approval fairness.</div></div></div>
    </div>
    <button class="btn btn-violet btn-full anim-5 mt-8" onclick="navigate('model-results')">Configure Audit →</button>
  `;
  return d;
}
