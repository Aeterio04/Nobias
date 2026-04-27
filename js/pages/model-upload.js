import { api } from '../api.js';
import { getState, setState } from '../store.js';

const uploadIcon = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`;
const checkIcon = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>`;
const spinnerIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>`;

export function modelUploadPage(nav) {
  const d = document.createElement('div');

  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Model Auditor</h1>
      <p class="page-subtitle">Upload your trained model and test dataset to audit for fairness.</p>
    </div>

    <div class="anim-2 mt-6" style="display:grid;grid-template-columns:1fr 1fr;gap:20px">

      <!-- Panel 1: Model -->
      <div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
          <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0">1</span>
          <span style="font-size:15px;font-weight:600;color:var(--c-text-1)">Your Trained Model</span>
        </div>
        <div id="model-zone" class="dropzone" style="min-height:180px;cursor:pointer;position:relative">
          <input type="file" id="model-input" accept=".pkl,.joblib,.onnx,.h5" style="display:none">
          <div id="model-idle">
            <div class="dropzone-icon">${uploadIcon}</div>
            <div class="dropzone-title">Drop model file here</div>
            <div class="dropzone-sub">or <span style="color:var(--c-accent);cursor:pointer">click to browse</span></div>
            <div class="dropzone-formats" style="margin-top:10px">
              <span class="format-badge">.PKL</span><span class="format-badge">.JOBLIB</span><span class="format-badge">.ONNX</span><span class="format-badge">.H5</span>
            </div>
          </div>
          <div id="model-loading" style="display:none;flex-direction:column;align-items:center;gap:10px">
            ${spinnerIcon}
            <span style="font-size:13px;color:var(--c-text-3)">Uploading...</span>
          </div>
          <div id="model-loaded" style="display:none;width:100%">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
              <div style="display:flex;align-items:center;gap:10px">
                <div style="width:36px;height:36px;border-radius:8px;background:var(--c-accent-violet-bg);display:flex;align-items:center;justify-content:center;color:var(--c-accent-violet);flex-shrink:0">${uploadIcon.replace('32','18').replace('32','18')}</div>
                <div>
                  <div id="model-filename" style="font-size:14px;font-weight:600;color:var(--c-text-1)"></div>
                  <div id="model-meta" style="font-size:12px;color:var(--c-text-4);margin-top:2px"></div>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">
                <span style="display:flex;align-items:center;gap:4px;font-size:11px;font-weight:600;color:var(--c-clear);background:var(--c-clear-bg);padding:3px 8px;border-radius:20px;border:1px solid var(--c-clear-bdr)">${checkIcon} Ready</span>
                <button id="model-replace" class="btn btn-ghost" style="font-size:12px;padding:4px 10px">Replace</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel 2: Test Data -->
      <div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
          <span style="background:var(--c-accent-violet-bg);color:var(--c-accent-violet);width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0">2</span>
          <span style="font-size:15px;font-weight:600;color:var(--c-text-1)">Test Dataset (CSV)</span>
        </div>
        <div id="testdata-zone" class="dropzone" style="min-height:180px;cursor:pointer;position:relative">
          <input type="file" id="testdata-input" accept=".csv,.xlsx,.xls" style="display:none">
          <div id="testdata-idle">
            <div class="dropzone-icon">${uploadIcon}</div>
            <div class="dropzone-title">Drop test CSV here</div>
            <div class="dropzone-sub">or <span style="color:var(--c-accent);cursor:pointer">click to browse</span></div>
            <div class="dropzone-formats" style="margin-top:10px">
              <span class="format-badge">.CSV</span><span class="format-badge">.XLSX</span>
            </div>
          </div>
          <div id="testdata-loading" style="display:none;flex-direction:column;align-items:center;gap:10px">
            ${spinnerIcon}
            <span style="font-size:13px;color:var(--c-text-3)">Uploading...</span>
          </div>
          <div id="testdata-loaded" style="display:none;width:100%">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
              <div style="display:flex;align-items:center;gap:10px">
                <div style="width:36px;height:36px;border-radius:8px;background:var(--c-accent-violet-bg);display:flex;align-items:center;justify-content:center;color:var(--c-accent-violet);flex-shrink:0">${uploadIcon.replace('32','18').replace('32','18')}</div>
                <div>
                  <div id="testdata-filename" style="font-size:14px;font-weight:600;color:var(--c-text-1)"></div>
                  <div id="testdata-meta" style="font-size:12px;color:var(--c-text-4);margin-top:2px"></div>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">
                <span style="display:flex;align-items:center;gap:4px;font-size:11px;font-weight:600;color:var(--c-clear);background:var(--c-clear-bg);padding:3px 8px;border-radius:20px;border:1px solid var(--c-clear-bdr)">${checkIcon} Ready</span>
                <button id="testdata-replace" class="btn btn-ghost" style="font-size:12px;padding:4px 10px">Replace</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compatibility banner -->
    <div id="compat-banner" style="display:none" class="anim-3 mt-4"></div>

    <!-- Config section — only shown after test data loaded -->
    <div id="config-section" style="display:none" class="anim-3 mt-8">
      <div class="config-grid">
        <div class="card">
          <div class="card-title">Protected Attributes</div>
          <p style="font-size:13px;color:var(--c-text-3);margin-bottom:16px">Columns representing sensitive or protected classes.</p>
          <div class="section-label">SELECTED</div>
          <div id="selected-attrs" style="min-height:32px;margin-bottom:12px"></div>
          <div class="section-label">AVAILABLE COLUMNS</div>
          <div id="available-cols"></div>
        </div>
        <div>
          <div class="card mb-4">
            <div class="card-title">Target Column</div>
            <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">The outcome variable to audit.</p>
            <select class="input select" id="target-select"></select>
          </div>
          <div class="card">
            <div class="card-title">Positive Outcome Value</div>
            <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">Value representing a favorable result (e.g. 1, Yes).</p>
            <input class="input" id="positive-input" value="1" placeholder="e.g. 1, Yes, True">
          </div>
        </div>
      </div>
    </div>

    <!-- Error banner -->
    <div id="error-banner" style="display:none;margin-top:16px;padding:12px 16px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:8px;color:var(--c-critical);font-size:14px"></div>

    <!-- Run button -->
    <div class="mt-8 anim-4" style="display:flex;justify-content:flex-end">
      <button id="run-btn" class="btn btn-violet" disabled style="opacity:0.4;cursor:not-allowed;min-width:200px">
        Run Model Audit →
      </button>
    </div>
  `;

  setTimeout(() => {
    const state = getState();

    // ── Element refs ──────────────────────────────────────────────────────
    const modelZone     = d.querySelector('#model-zone');
    const modelInput    = d.querySelector('#model-input');
    const modelIdle     = d.querySelector('#model-idle');
    const modelLoading  = d.querySelector('#model-loading');
    const modelLoaded   = d.querySelector('#model-loaded');
    const modelReplace  = d.querySelector('#model-replace');

    const testZone      = d.querySelector('#testdata-zone');
    const testInput     = d.querySelector('#testdata-input');
    const testIdle      = d.querySelector('#testdata-idle');
    const testLoading   = d.querySelector('#testdata-loading');
    const testLoaded    = d.querySelector('#testdata-loaded');
    const testReplace   = d.querySelector('#testdata-replace');

    const compatBanner  = d.querySelector('#compat-banner');
    const configSection = d.querySelector('#config-section');
    const errorBanner   = d.querySelector('#error-banner');
    const runBtn        = d.querySelector('#run-btn');

    const selectedAttrs = new Set();

    // ── Helpers ───────────────────────────────────────────────────────────
    function showError(msg) {
      errorBanner.textContent = msg;
      errorBanner.style.display = 'block';
    }
    function clearError() {
      errorBanner.style.display = 'none';
    }

    function setModelState(s, data) {
      modelIdle.style.display    = s === 'idle'    ? '' : 'none';
      modelLoading.style.display = s === 'loading' ? 'flex' : 'none';
      modelLoaded.style.display  = s === 'loaded'  ? 'flex' : 'none';
      if (s === 'loaded' && data) {
        d.querySelector('#model-filename').textContent = data.filename;
        d.querySelector('#model-meta').textContent = `${data.model_type || 'Model'} · ${data.file_size_mb} MB`;
      }
    }

    function setTestState(s, data) {
      testIdle.style.display    = s === 'idle'    ? '' : 'none';
      testLoading.style.display = s === 'loading' ? 'flex' : 'none';
      testLoaded.style.display  = s === 'loaded'  ? 'flex' : 'none';
      if (s === 'loaded' && data) {
        d.querySelector('#testdata-filename').textContent = data.filename;
        d.querySelector('#testdata-meta').textContent = `${data.row_count} rows · ${data.column_count} columns`;
        showConfigSection(data.columns);
      }
    }

    function showConfigSection(columns) {
      configSection.style.display = 'block';
      const targetSelect = d.querySelector('#target-select');
      targetSelect.innerHTML = columns.map(c => `<option value="${c}">${c}</option>`).join('');
      renderAttrs(columns);
    }

    function renderAttrs(columns) {
      const cols = columns || getState().testDataUpload?.columns || [];
      const selectedDiv  = d.querySelector('#selected-attrs');
      const availableDiv = d.querySelector('#available-cols');

      selectedDiv.innerHTML = selectedAttrs.size > 0
        ? Array.from(selectedAttrs).map(a =>
            `<span class="chip">${a} <span class="chip-remove" data-attr="${a}" style="cursor:pointer;margin-left:4px">×</span></span>`
          ).join('')
        : '<span style="color:var(--c-text-5);font-size:13px">No attributes selected</span>';

      availableDiv.innerHTML = cols
        .filter(c => !selectedAttrs.has(c))
        .map(c => `<span class="chip-outline chip" data-attr="${c}" style="cursor:pointer"><span style="color:var(--c-accent);margin-right:4px">+</span>${c}</span>`)
        .join('');

      selectedDiv.querySelectorAll('.chip-remove').forEach(el => {
        el.onclick = (e) => { e.stopPropagation(); selectedAttrs.delete(el.dataset.attr); renderAttrs(); updateRunBtn(); };
      });
      availableDiv.querySelectorAll('.chip-outline').forEach(el => {
        el.onclick = () => { selectedAttrs.add(el.dataset.attr); renderAttrs(); updateRunBtn(); };
      });
    }

    function updateRunBtn() {
      const s = getState();
      const ready = s.modelUpload && s.testDataUpload && selectedAttrs.size > 0;
      runBtn.disabled = !ready;
      runBtn.style.opacity = ready ? '1' : '0.4';
      runBtn.style.cursor  = ready ? 'pointer' : 'not-allowed';
    }

    async function checkCompatibility() {
      const s = getState();
      if (!s.modelUpload || !s.testDataUpload) return;
      try {
        const compat = await api.model.checkCompatibility(
          s.modelUpload.tmp_path,
          s.testDataUpload.tmp_path
        );
        const ok = compat.compatible !== false;
        compatBanner.style.display = 'block';
        compatBanner.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:8px;
            background:${ok ? 'var(--c-clear-bg)' : 'var(--c-moderate-bg)'};
            border:1px solid ${ok ? 'var(--c-clear-bdr)' : 'var(--c-moderate-bdr)'};
            font-size:13px;color:${ok ? 'var(--c-clear)' : 'var(--c-moderate)'}">
            ${ok ? checkIcon : '⚠'}
            <span>Feature compatibility: <strong>${compat.matching_features ?? '?'}/${compat.total_features ?? '?'} features matched</strong>
            ${compat.missing_from_test?.length > 0 ? ` · Missing: ${compat.missing_from_test.slice(0,3).join(', ')}` : ''}</span>
          </div>`;
      } catch (_) { /* non-fatal */ }
    }

    // ── Upload handlers ───────────────────────────────────────────────────
    async function handleModelUpload(file) {
      clearError();
      setModelState('loading');
      try {
        const result = await api.model.uploadModel(file);
        setState({ modelUpload: result });
        setModelState('loaded', result);
        checkCompatibility();
        updateRunBtn();
      } catch (err) {
        setModelState('idle');
        showError(`Model upload failed: ${err.message}`);
      }
    }

    async function handleTestUpload(file) {
      clearError();
      setTestState('loading');
      try {
        const result = await api.model.uploadTestData(file);
        setState({ testDataUpload: result });
        setTestState('loaded', result);
        checkCompatibility();
        updateRunBtn();
      } catch (err) {
        setTestState('idle');
        showError(`Test data upload failed: ${err.message}`);
      }
    }

    // ── Wire drop zones ───────────────────────────────────────────────────
    function wireZone(zone, input, handler) {
      zone.addEventListener('click', (e) => {
        if (e.target.closest('button')) return;
        input.click();
      });
      input.addEventListener('change', (e) => { if (e.target.files[0]) handler(e.target.files[0]); });
      zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
      zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
      zone.addEventListener('drop', (e) => {
        e.preventDefault(); zone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) handler(e.dataTransfer.files[0]);
      });
    }

    wireZone(modelZone, modelInput, handleModelUpload);
    wireZone(testZone,  testInput,  handleTestUpload);

    modelReplace.addEventListener('click', () => {
      setState({ modelUpload: null });
      setModelState('idle');
      compatBanner.style.display = 'none';
      updateRunBtn();
    });

    testReplace.addEventListener('click', () => {
      setState({ testDataUpload: null });
      setTestState('idle');
      configSection.style.display = 'none';
      compatBanner.style.display = 'none';
      selectedAttrs.clear();
      updateRunBtn();
    });

    // ── Run button ────────────────────────────────────────────────────────
    runBtn.addEventListener('click', () => {
      clearError();
      const s = getState();
      if (!s.modelUpload || !s.testDataUpload) return;
      if (selectedAttrs.size === 0) { showError('Select at least one protected attribute.'); return; }

      const targetColumn  = d.querySelector('#target-select').value;
      const positiveValue = d.querySelector('#positive-input').value.trim() || '1';

      setState({
        modelConfig: {
          model_path:           s.modelUpload.tmp_path,
          testdata_path:        s.testDataUpload.tmp_path,
          protected_attributes: Array.from(selectedAttrs),
          target_column:        targetColumn,
          positive_value:       positiveValue,
        },
        modelResult: null,
      });

      nav('model-running');
    });

    // ── Restore state if already uploaded ─────────────────────────────────
    if (state.modelUpload) {
      setModelState('loaded', state.modelUpload);
    }
    if (state.testDataUpload) {
      setTestState('loaded', state.testDataUpload);
      if (state.modelUpload) checkCompatibility();
    }
    updateRunBtn();

  }, 0);

  return d;
}
