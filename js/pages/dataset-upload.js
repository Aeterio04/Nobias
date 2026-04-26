// ── Dataset Upload Page — Redesigned ──
export function datasetUploadPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Dataset Auditor</h1>
      <p class="page-subtitle">Upload your dataset to begin a bias audit.</p>
    </div>
    <div class="anim-2">
      <div class="dropzone" id="dropzone-main">
        <div class="dropzone-icon"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
        <div class="dropzone-title">Drag & drop your dataset here</div>
        <div class="dropzone-sub">or <a href="#" class="dropzone-link" onclick="event.preventDefault()">click to browse files</a></div>
        <div class="dropzone-formats">
          <span class="format-badge">CSV</span><span class="format-badge">XLSX</span><span class="format-badge">Parquet</span>
        </div>
        <div class="dropzone-limit">Max 500MB</div>
      </div>
    </div>
    <div class="divider-text anim-3">or try a sample dataset</div>
    <div class="grid-3 anim-3">
      <div class="sample-card" onclick="document.getElementById('file-loaded').style.display='flex';document.getElementById('dropzone-main').style.display='none'">
        <div class="sample-card-title">COMPAS Recidivism</div>
        <div class="sample-card-desc">Bias evaluation in criminal justice</div>
        <a href="#" class="btn-ghost" onclick="event.preventDefault()">Load Sample →</a>
      </div>
      <div class="sample-card">
        <div class="sample-card-title">Adult Census Income</div>
        <div class="sample-card-desc">Predicting income thresholds</div>
        <a href="#" class="btn-ghost" onclick="event.preventDefault()">Load Sample →</a>
      </div>
      <div class="sample-card">
        <div class="sample-card-title">German Credit</div>
        <div class="sample-card-desc">Risk assessment and fairness</div>
        <a href="#" class="btn-ghost" onclick="event.preventDefault()">Load Sample →</a>
      </div>
    </div>
    <div class="anim-4 mt-8" id="file-loaded" style="display:flex">
      <div class="file-loaded" style="width:100%">
        <div class="file-loaded-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
        <div class="file-loaded-info">
          <div class="file-loaded-name">hiring_data.csv <span class="badge badge-clear" style="margin-left:8px;font-size:10px">FILE READY</span></div>
          <div class="file-loaded-meta">12,847 rows · 14 columns · 2.3 MB</div>
        </div>
        <div class="file-loaded-actions">
          <button class="btn btn-ghost" style="color:var(--c-text-3)">Replace</button>
          <button class="btn btn-primary" onclick="navigate('dataset-configure')">Configure Dataset →</button>
        </div>
      </div>
    </div>
  `;
  return d;
}
