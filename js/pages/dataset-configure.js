// ── Dataset Configure — Redesigned ──
export function datasetConfigurePage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <div class="file-loaded mb-8">
        <div class="file-loaded-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
        <div class="file-loaded-info">
          <div class="file-loaded-name">hiring_data.csv</div>
          <div class="file-loaded-meta">12,847 rows · 14 columns</div>
        </div>
        <span class="badge badge-clear">FILE LOADED</span>
      </div>
    </div>
    <div class="config-grid anim-2">
      <div class="card">
        <div class="card-title" style="display:flex;align-items:center;gap:8px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg> Protected Attributes</div>
        <p style="font-size:13px;color:var(--c-text-3);margin-bottom:16px">Select the columns representing sensitive or protected classes to evaluate for bias.</p>
        <div class="section-label">SELECTED ATTRIBUTES</div>
        <div class="selected-attrs">
          <span class="chip">gender <span class="chip-remove">×</span></span>
          <span class="chip">race <span class="chip-remove">×</span></span>
          <span class="chip">age <span class="chip-remove">×</span></span>
        </div>
        <div class="section-label" style="margin-top:16px">AVAILABLE COLUMNS</div>
        <div class="available-cols">
          <span class="chip-outline chip"><span class="plus" style="font-size:12px;opacity:0.6">+</span> gpa</span>
          <span class="chip-outline chip"><span class="plus" style="font-size:12px;opacity:0.6">+</span> exp</span>
          <span class="chip-outline chip"><span class="plus" style="font-size:12px;opacity:0.6">+</span> name</span>
          <span class="chip-outline chip"><span class="plus" style="font-size:12px;opacity:0.6">+</span> hired</span>
        </div>
      </div>
      <div>
        <div class="card mb-4">
          <div class="card-title" style="display:flex;align-items:center;gap:8px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5"><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83"/></svg> Target Column</div>
          <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">The outcome variable you want to audit.</p>
          <select class="input select"><option>hired</option><option>approved</option></select>
        </div>
        <div class="card">
          <div class="card-title">Positive Outcome</div>
          <p style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">What value represents a favorable result.</p>
          <select class="input select"><option>Yes</option><option>No</option></select>
        </div>
      </div>
    </div>
    <div class="section anim-3 mt-8">
      <div class="card">
        <div class="section-label">DATA PREVIEW (FIRST 5 ROWS)</div>
        <div class="table-container" style="box-shadow:none;border:none">
          <table class="table">
            <thead><tr>
              <th>name</th><th>gender <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--c-accent);vertical-align:middle;margin-left:4px"></span></th><th>race <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--c-accent);vertical-align:middle;margin-left:4px"></span></th>
              <th>age <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--c-accent);vertical-align:middle;margin-left:4px"></span></th><th>gpa</th><th>exp</th><th>hired <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--c-clear);vertical-align:middle;margin-left:4px"></span></th>
            </tr></thead>
            <tbody>
              <tr><td class="mono">Sarah J.</td><td>Female</td><td>Caucasian</td><td>28</td><td class="mono">3.8</td><td class="mono">4</td><td style="color:var(--c-clear);font-weight:500">Yes</td></tr>
              <tr><td class="mono">Marcus T.</td><td>Male</td><td>African American</td><td>32</td><td class="mono">3.5</td><td class="mono">6</td><td style="color:var(--c-clear);font-weight:500">Yes</td></tr>
              <tr><td class="mono">Elena R.</td><td>Female</td><td>Hispanic</td><td>24</td><td class="mono">3.9</td><td class="mono">1</td><td style="color:var(--c-critical);font-weight:500">No</td></tr>
              <tr><td class="mono">David K.</td><td>Male</td><td>Caucasian</td><td>45</td><td class="mono">3.2</td><td class="mono">15</td><td style="color:var(--c-clear);font-weight:500">Yes</td></tr>
              <tr><td class="mono">Priya M.</td><td>Female</td><td>Asian</td><td>29</td><td class="mono">3.7</td><td class="mono">5</td><td style="color:var(--c-clear);font-weight:500">Yes</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="anim-4 mt-8">
      <div class="section-title mb-4">Audit Mode</div>
      <div class="segmented">
        <button class="segmented-opt">⚡ Quick</button>
        <button class="segmented-opt active">Standard</button>
        <button class="segmented-opt">Full</button>
      </div>
    </div>
    <div class="anim-5 mt-8" style="display:flex;justify-content:space-between;align-items:center;padding-top:24px;border-top:1px solid var(--c-border-row)">
      <button class="btn btn-secondary" onclick="navigate('dataset-upload')">← Back to Upload</button>
      <button class="btn btn-primary" onclick="navigate('dataset-running')">Run Audit →</button>
    </div>
  `;
  return d;
}
