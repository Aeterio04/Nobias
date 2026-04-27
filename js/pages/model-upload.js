// ── Model Upload — Redesigned ──
import { api } from '../api.js';
import { getState, setState } from '../store.js';

export function modelUploadPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  
  d.innerHTML = `
    <div class="anim-1"><h1 class="page-title">Model Auditor</h1><p class="page-subtitle">Upload your trained model and test dataset to audit for fairness.</p></div>
    <div class="card anim-2 mt-6">
      <div class="model-upload-grid">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600">1</span>
            <span style="font-size:16px;font-weight:600;color:var(--c-text-1)">Your Trained Model</span>
          </div>
          <div class="dropzone" id="model-dropzone" style="padding:40px 24px">
            <input type="file" id="model-file-input" accept=".pkl,.joblib,.onnx,.h5" style="display:none" />
            <div class="dropzone-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
            <div class="dropzone-title" style="font-size:14px">${state.modelUpload ? state.modelUpload.filename : 'Drop your model file here'}</div>
            <div class="dropzone-sub">or <a href="#" class="dropzone-link" id="model-browse-link">click to browse</a></div>
            <div class="dropzone-formats" style="margin-top:8px"><span class="format-badge">.PKL</span><span class="format-badge">.JOBLIB</span><span class="format-badge">.ONNX</span><span class="format-badge">.H5</span></div>
          </div>
        </div>
        <div class="model-plus">+</div>
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600">2</span>
            <span style="font-size:16px;font-weight:600;color:var(--c-text-1)">Test Dataset (CSV)</span>
          </div>
          <div class="dropzone" id="testdata-dropzone" style="padding:40px 24px">
            <input type="file" id="testdata-file-input" accept=".csv,.xlsx" style="display:none" />
            <div class="dropzone-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
            <div class="dropzone-title" style="font-size:14px">${state.testDataUpload ? state.testDataUpload.filename : 'Drop your test CSV here'}</div>
            <div class="dropzone-sub">Same features as your model + ground truth labels</div>
            <div class="dropzone-formats" style="margin-top:8px"><span class="format-badge">.CSV</span><span class="format-badge">.XLSX</span></div>
          </div>
        </div>
      </div>
    </div>
    <div id="compat-banner" style="display:none" class="compat-banner compat-success anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg><span id="compat-message">Checking compatibility...</span></div>
    <div id="error-banner" style="display:none" class="compat-banner compat-error anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg><span id="error-message"></span></div>
    <button id="configure-btn" class="btn btn-violet btn-full anim-5 mt-8" style="display:none">Configure Audit →</button>
  `;
  
  setTimeout(() => {
    const modelInput = d.querySelector('#model-file-input');
    const testdataInput = d.querySelector('#testdata-file-input');
    const modelDropzone = d.querySelector('#model-dropzone');
    const testdataDropzone = d.querySelector('#testdata-dropzone');
    const modelBrowseLink = d.querySelector('#model-browse-link');
    const compatBanner = d.querySelector('#compat-banner');
    const errorBanner = d.querySelector('#error-banner');
    const configureBtn = d.querySelector('#configure-btn');
    
    modelBrowseLink?.addEventListener('click', (e) => {
      e.preventDefault();
      modelInput.click();
    });
    
    modelDropzone?.addEventListener('click', () => modelInput.click());
    modelDropzone?.addEventListener('dragover', (e) => {
      e.preventDefault();
      modelDropzone.style.borderColor = 'var(--c-accent-violet)';
    });
    modelDropzone?.addEventListener('dragleave', () => {
      modelDropzone.style.borderColor = '';
    });
    modelDropzone?.addEventListener('drop', async (e) => {
      e.preventDefault();
      modelDropzone.style.borderColor = '';
      const file = e.dataTransfer.files[0];
      if (file) await handleModelUpload(file);
    });
    
    modelInput?.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) await handleModelUpload(file);
    });
    
    testdataDropzone?.addEventListener('click', () => testdataInput.click());
    testdataDropzone?.addEventListener('dragover', (e) => {
      e.preventDefault();
      testdataDropzone.style.borderColor = 'var(--c-accent-violet)';
    });
    testdataDropzone?.addEventListener('dragleave', () => {
      testdataDropzone.style.borderColor = '';
    });
    testdataDropzone?.addEventListener('drop', async (e) => {
      e.preventDefault();
      testdataDropzone.style.borderColor = '';
      const file = e.dataTransfer.files[0];
      if (file) await handleTestDataUpload(file);
    });
    
    testdataInput?.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) await handleTestDataUpload(file);
    });
    
    async function handleModelUpload(file) {
      try {
        errorBanner.style.display = 'none';
        const result = await api.model.uploadModel(file);
        setState({ modelUpload: result, modelError: null });
        d.querySelector('.dropzone-title').textContent = result.filename;
        checkCompatibility();
      } catch (err) {
        setState({ modelError: err.message });
        errorBanner.style.display = 'flex';
        d.querySelector('#error-message').textContent = `Model upload failed: ${err.message}`;
      }
    }
    
    async function handleTestDataUpload(file) {
      try {
        errorBanner.style.display = 'none';
        const result = await api.model.uploadTestData(file);
        setState({ testDataUpload: result, modelError: null });
        d.querySelectorAll('.dropzone-title')[1].textContent = result.filename;
        checkCompatibility();
      } catch (err) {
        setState({ modelError: err.message });
        errorBanner.style.display = 'flex';
        d.querySelector('#error-message').textContent = `Test data upload failed: ${err.message}`;
      }
    }
    
    async function checkCompatibility() {
      const state = getState();
      if (state.modelUpload && state.testDataUpload) {
        try {
          const compat = await api.model.checkCompatibility(
            state.modelUpload.model_path || state.modelUpload.tmp_path,
            state.testDataUpload.tmp_path
          );
          setState({ compatibility: compat });
          compatBanner.style.display = 'flex';
          d.querySelector('#compat-message').innerHTML = `Feature compatibility: <strong>${compat.matching_features || compat.matched || '?'}/${compat.total_features || compat.total || '?'} features match</strong>`;
          configureBtn.style.display = 'block';
          configureBtn.onclick = () => nav('model-results');
        } catch (err) {
          errorBanner.style.display = 'flex';
          d.querySelector('#error-message').textContent = `Compatibility check failed: ${err.message}`;
        }
      }
    }
    
    if (state.modelUpload && state.testDataUpload) {
      checkCompatibility();
    }
  }, 0);
  
  return d;
}
