// ── Settings Page — Redesigned ──
export function settingsPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="settings-content">
      <div class="anim-1">
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure your LLM backend, defaults, and appearance.</p>
      </div>
      <div class="settings-card anim-2">
        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg> LLM Backend</h3>
        <div class="form-group">
          <label class="form-label">LLM Provider</label>
          <select class="input select"><option>OpenAI</option><option>Anthropic</option><option>Google</option><option>Ollama (Local)</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">API Key</label>
          <div style="display:flex;gap:12px">
            <div class="api-key-input" style="flex:1">
              <input type="password" class="input" value="sk-••••••••••••••••••••••••••••••••" />
              <button class="api-key-toggle">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
            <button class="btn btn-secondary">Test Connection</button>
          </div>
        </div>
        <div class="compat-banner compat-success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>
          <span>Connected — GPT-4o available</span>
        </div>
      </div>
      <div class="settings-card anim-3">
        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-teal)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Audit Defaults</h3>
        <div class="form-group">
          <label class="form-label">Default Audit Mode</label>
          <div class="segmented">
            <button class="segmented-opt">Quick</button>
            <button class="segmented-opt active">Standard</button>
            <button class="segmented-opt">Full</button>
          </div>
        </div>
        <hr style="border:none;border-top:1px solid var(--c-border-row);margin:16px 0">
        <div class="form-group" style="margin-bottom:0">
          <label class="form-label">Default Export Format</label>
          <div class="checkbox-row"><div class="checkbox checked">✓</div><span class="checkbox-label">PDF</span></div>
          <div class="checkbox-row"><div class="checkbox checked">✓</div><span class="checkbox-label">JSON</span></div>
          <div class="checkbox-row"><div class="checkbox"></div><span class="checkbox-label">CAFFE JSON</span></div>
        </div>
      </div>
      <div class="settings-card anim-4">
        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-violet)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r="2.5"/><path d="M17 2H7a5 5 0 0 0-5 5v10a5 5 0 0 0 5 5h10a5 5 0 0 0 5-5V7a5 5 0 0 0-5-5z"/></svg> Appearance</h3>
        <p style="font-size:13px;color:var(--c-text-4)">Theme and display preferences (coming soon).</p>
      </div>
      <div class="settings-saved anim-5">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#30D158" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>
        Settings saved
      </div>
    </div>
  `;
  return d;
}
