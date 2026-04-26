import { api } from '../api.js';
import { getState, setState } from '../store.js';

export function settingsPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="settings-content">
      <div class="anim-1">
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure your LLM backend, defaults, and appearance.</p>
      </div>
      <div class="settings-card anim-2">
        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v6M12 17v6M5.64 5.64l4.24 4.24M14.12 14.12l4.24 4.24M1 12h6M17 12h6M5.64 18.36l4.24-4.24M14.12 9.88l4.24-4.24"/></svg> LLM Backend</h3>
        <div class="form-group">
          <label class="form-label">LLM Provider</label>
          <select class="input select" id="llm-provider">
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="google">Google</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">API Key</label>
          <div style="display:flex;gap:12px">
            <div class="api-key-input" style="flex:1">
              <input type="password" class="input" id="api-key" placeholder="Enter your API key">
              <button class="api-key-toggle" id="toggle-key">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
            <button class="btn btn-secondary" id="test-btn">Test Connection</button>
          </div>
        </div>
        <div id="connection-status" style="display:none;margin-top:12px"></div>
      </div>
      <div class="settings-card anim-3">
        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-teal)" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Audit Defaults</h3>
        <div class="form-group">
          <label class="form-label">Default Audit Mode</label>
          <div class="segmented" id="audit-mode">
            <button class="segmented-opt" data-mode="quick">Quick</button>
            <button class="segmented-opt active" data-mode="standard">Standard</button>
            <button class="segmented-opt" data-mode="full">Full</button>
          </div>
        </div>
      </div>
      <div id="save-indicator" class="settings-saved" style="display:none">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#30D158" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>
        Settings saved
      </div>
    </div>
  `;
  
  setTimeout(async () => {
    try {
      const settings = await api.settings.get();
      setState({ settings });
      
      d.querySelector('#llm-provider').value = settings.llm_provider || 'openai';
      d.querySelector('#api-key').value = settings.api_key ? '••••••••••••••••' : '';
      
      d.querySelectorAll('#audit-mode button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === settings.default_audit_mode);
      });
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
    
    const showSaved = () => {
      const indicator = d.querySelector('#save-indicator');
      indicator.style.display = 'flex';
      setTimeout(() => indicator.style.display = 'none', 2000);
    };
    
    d.querySelector('#llm-provider').onchange = async (e) => {
      try {
        await api.settings.update({ llm_provider: e.target.value });
        showSaved();
      } catch (err) {
        alert('Failed to save: ' + err.message);
      }
    };
    
    d.querySelector('#api-key').onblur = async (e) => {
      if (e.target.value && !e.target.value.includes('•')) {
        try {
          await api.settings.update({ api_key: e.target.value });
          showSaved();
        } catch (err) {
          alert('Failed to save: ' + err.message);
        }
      }
    };
    
    d.querySelector('#toggle-key').onclick = () => {
      const input = d.querySelector('#api-key');
      input.type = input.type === 'password' ? 'text' : 'password';
    };
    
    d.querySelector('#test-btn').onclick = async () => {
      const statusDiv = d.querySelector('#connection-status');
      statusDiv.textContent = 'Testing...';
      statusDiv.style.display = 'block';
      statusDiv.className = '';
      
      try {
        const result = await api.settings.testConnection();
        statusDiv.className = result.connected ? 'compat-banner compat-success' : 'compat-banner';
        statusDiv.style.background = result.connected ? 'var(--c-clear-bg)' : 'var(--c-critical-bg)';
        statusDiv.style.borderColor = result.connected ? 'var(--c-clear-bdr)' : 'var(--c-critical-bdr)';
        statusDiv.style.color = result.connected ? '#065F46' : 'var(--c-critical)';
        statusDiv.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="${result.connected ? 'M20 6 9 17l-5-5' : 'M18 6 6 18M6 6l12 12'}"/></svg><span>${result.message}</span>`;
      } catch (err) {
        statusDiv.className = 'compat-banner';
        statusDiv.style.background = 'var(--c-critical-bg)';
        statusDiv.textContent = 'Connection failed: ' + err.message;
      }
    };
    
    d.querySelectorAll('#audit-mode button').forEach(btn => {
      btn.onclick = async () => {
        d.querySelectorAll('#audit-mode button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        try {
          await api.settings.update({ default_audit_mode: btn.dataset.mode });
          showSaved();
        } catch (err) {
          alert('Failed to save: ' + err.message);
        }
      };
    });
  }, 0);
  
  return d;
}
