import { api } from '../api.js';
import { setState, getState } from '../store.js';

export function datasetUploadPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Dataset Auditor</h1>
      <p class="page-subtitle">Upload your dataset to begin a bias audit.</p>
    </div>
    <div class="anim-2">
      <div class="dropzone" id="dropzone-main">
        <div class="dropzone-icon"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
        <div class="dropzone-title">Drag & drop your dataset here</div>
        <div class="dropzone-sub">or <a href="#" class="dropzone-link" id="browse-link">click to browse files</a></div>
        <div class="dropzone-formats">
          <span class="format-badge">CSV</span><span class="format-badge">XLSX</span><span class="format-badge">Parquet</span>
        </div>
        <div class="dropzone-limit">Max 500MB</div>
        <input type="file" id="file-input" accept=".csv,.xlsx,.xls,.parquet" style="display:none">
      </div>
      <div id="upload-error" style="display:none;margin-top:16px;padding:12px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:8px;color:var(--c-critical)"></div>
    </div>
    <div class="divider-text anim-3">or try a sample dataset</div>
    <div class="grid-3 anim-3">
      <div class="sample-card" data-sample="compas">
        <div class="sample-card-title">COMPAS Recidivism</div>
        <div class="sample-card-desc">Bias evaluation in criminal justice</div>
        <a href="#" class="btn-ghost">Load Sample →</a>
      </div>
      <div class="sample-card" data-sample="adult_census">
        <div class="sample-card-title">Adult Census Income</div>
        <div class="sample-card-desc">Predicting income thresholds</div>
        <a href="#" class="btn-ghost">Load Sample →</a>
      </div>
      <div class="sample-card" data-sample="german_credit">
        <div class="sample-card-title">German Credit</div>
        <div class="sample-card-desc">Risk assessment and fairness</div>
        <a href="#" class="btn-ghost">Load Sample →</a>
      </div>
    </div>
    <div class="anim-4 mt-8" id="file-loaded" style="display:none">
      <div class="file-loaded" style="width:100%">
        <div class="file-loaded-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
        <div class="file-loaded-info">
          <div class="file-loaded-name" id="file-name">Loading...</div>
          <div class="file-loaded-meta" id="file-meta"></div>
        </div>
        <div class="file-loaded-actions">
          <button class="btn btn-ghost" id="replace-btn">Replace</button>
          <button class="btn btn-primary" id="configure-btn">Configure Dataset →</button>
        </div>
      </div>
    </div>
  `;
  
  setTimeout(() => {
    const dropzone = d.querySelector('#dropzone-main');
    const fileInput = d.querySelector('#file-input');
    const browseLink = d.querySelector('#browse-link');
    const fileLoaded = d.querySelector('#file-loaded');
    const errorDiv = d.querySelector('#upload-error');
    
    const handleFile = async (file) => {
      try {
        errorDiv.style.display = 'none';
        dropzone.innerHTML = '<div style="padding:40px;text-align:center">Uploading...</div>';
        const result = await api.dataset.upload(file);
        setState({ datasetUpload: result });
        d.querySelector('#file-name').textContent = result.filename;
        d.querySelector('#file-meta').textContent = `${result.row_count} rows · ${result.column_count} columns · ${result.file_size_mb} MB`;
        dropzone.style.display = 'none';
        fileLoaded.style.display = 'flex';
      } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = 'block';
        dropzone.innerHTML = d.querySelector('#dropzone-main').innerHTML;
      }
    };
    
    browseLink.onclick = (e) => { e.preventDefault(); fileInput.click(); };
    fileInput.onchange = (e) => { if (e.target.files[0]) handleFile(e.target.files[0]); };
    
    dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); };
    dropzone.ondragleave = () => dropzone.classList.remove('drag-over');
    dropzone.ondrop = (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
      if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    };
    
    d.querySelector('#replace-btn')?.addEventListener('click', () => {
      setState({ datasetUpload: null });
      dropzone.style.display = 'flex';
      fileLoaded.style.display = 'none';
    });
    
    d.querySelector('#configure-btn')?.addEventListener('click', () => nav('dataset-configure'));
    
    d.querySelectorAll('.sample-card').forEach(card => {
      card.onclick = async () => {
        try {
          errorDiv.style.display = 'none';
          const result = await api.dataset.loadSample(card.dataset.sample);
          setState({ datasetUpload: result });
          d.querySelector('#file-name').textContent = result.filename;
          d.querySelector('#file-meta').textContent = `${result.row_count} rows · ${result.column_count} columns`;
          dropzone.style.display = 'none';
          fileLoaded.style.display = 'flex';
        } catch (err) {
          errorDiv.textContent = err.message;
          errorDiv.style.display = 'block';
        }
      };
    });
    
    const state = getState();
    if (state.datasetUpload) {
      d.querySelector('#file-name').textContent = state.datasetUpload.filename;
      d.querySelector('#file-meta').textContent = `${state.datasetUpload.row_count} rows · ${state.datasetUpload.column_count} columns`;
      dropzone.style.display = 'none';
      fileLoaded.style.display = 'flex';
    }
  }, 0);
  
  return d;
}
