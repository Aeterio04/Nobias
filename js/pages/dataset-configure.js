import { getState, setState } from '../store.js';

export function datasetConfigurePage(nav) {
  const state = getState();
  const upload = state.datasetUpload;
  
  if (!upload) {
    nav('dataset-upload');
    return document.createElement('div');
  }
  
  const d = document.createElement('div');
  const selectedAttrs = upload.suggested_protected_attributes || [];
  const targetCol = upload.suggested_target_column || upload.columns[0];
  const posVal = upload.suggested_positive_value || '1';
  
  d.innerHTML = `
    <div class="anim-1">
      <div class="file-loaded mb-8">
        <div class="file-loaded-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
        <div class="file-loaded-info">
          <div class="file-loaded-name">${upload.filename}</div>
          <div class="file-loaded-meta">${upload.row_count} rows · ${upload.column_count} columns</div>
        </div>
        <span class="badge badge-clear">FILE LOADED</span>
      </div>
    </div>
    <div class="config-grid anim-2">
      <div class="card">
        <div class="card-title">Protected Attributes</div>
        <p style="font-size:13px;color:var(--c-text-3);margin-bottom:16px">Select columns representing sensitive or protected classes.</p>
        <div class="section-label">SELECTED ATTRIBUTES</div>
        <div class="selected-attrs" id="selected-attrs"></div>
        <div class="section-label" style="margin-top:16px">AVAILABLE COLUMNS</div>
        <div class="available-cols" id="available-cols"></div>
      </div>
      <div>
        <div class="card mb-4">
          <div class="card-title">Target Column</div>
          <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">The outcome variable to audit.</p>
          <select class="input select" id="target-select">
            ${upload.columns.map(c => `<option ${c === targetCol ? 'selected' : ''}>${c}</option>`).join('')}
          </select>
        </div>
        <div class="card">
          <div class="card-title">Positive Outcome</div>
          <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">Value representing favorable result.</p>
          <input class="input" id="positive-input" value="${posVal}" placeholder="e.g., 1, Yes, True">
        </div>
      </div>
    </div>
    <div class="anim-3 mt-8">
      <div class="section-title mb-4">Audit Mode</div>
      <div class="segmented" id="audit-mode">
        <button class="segmented-opt" data-mode="quick">⚡ Quick</button>
        <button class="segmented-opt active" data-mode="standard">Standard</button>
        <button class="segmented-opt" data-mode="full">Full</button>
      </div>
    </div>
    <div id="error-banner" style="display:none;margin-top:24px;padding:12px;background:var(--c-critical-bg);border:1px solid var(--c-critical-bdr);border-radius:8px;color:var(--c-critical)"></div>
    <div class="anim-5 mt-8" style="display:flex;justify-content:space-between;align-items:center;padding-top:24px;border-top:1px solid var(--c-border-row)">
      <button class="btn btn-secondary" id="back-btn">← Back to Upload</button>
      <button class="btn btn-primary" id="run-btn">Run Audit →</button>
    </div>
  `;
  
  setTimeout(() => {
    const selected = new Set(selectedAttrs);
    let auditMode = 'standard';
    
    const renderAttrs = () => {
      const selectedDiv = d.querySelector('#selected-attrs');
      const availableDiv = d.querySelector('#available-cols');
      selectedDiv.innerHTML = Array.from(selected).map(a => 
        `<span class="chip">${a} <span class="chip-remove" data-attr="${a}">×</span></span>`
      ).join('') || '<span style="color:var(--c-text-5);font-size:13px">No attributes selected</span>';
      availableDiv.innerHTML = upload.columns.filter(c => !selected.has(c)).map(c =>
        `<span class="chip-outline chip" data-attr="${c}"><span class="plus">+</span> ${c}</span>`
      ).join('');
      
      selectedDiv.querySelectorAll('.chip-remove').forEach(el => {
        el.onclick = () => { selected.delete(el.dataset.attr); renderAttrs(); };
      });
      availableDiv.querySelectorAll('.chip-outline').forEach(el => {
        el.onclick = () => { selected.add(el.dataset.attr); renderAttrs(); };
      });
    };
    
    renderAttrs();
    
    d.querySelectorAll('#audit-mode button').forEach(btn => {
      btn.onclick = () => {
        d.querySelectorAll('#audit-mode button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        auditMode = btn.dataset.mode;
      };
    });
    
    d.querySelector('#back-btn').onclick = () => nav('dataset-upload');
    
    d.querySelector('#run-btn').onclick = async () => {
      const errorBanner = d.querySelector('#error-banner');
      errorBanner.style.display = 'none';
      
      if (selected.size === 0) {
        errorBanner.textContent = 'Please select at least one protected attribute';
        errorBanner.style.display = 'block';
        return;
      }
      
      const targetColumn = d.querySelector('#target-select').value;
      const positiveValue = d.querySelector('#positive-input').value.trim();
      
      if (!positiveValue) {
        errorBanner.textContent = 'Please enter a positive outcome value';
        errorBanner.style.display = 'block';
        return;
      }
      
      setState({
        datasetConfig: {
          protected_attributes: Array.from(selected),
          target_column: targetColumn,
          positive_value: positiveValue,
          audit_mode: auditMode,
        }
      });
      
      nav('dataset-running');
    };
  }, 0);
  
  return d;
}
