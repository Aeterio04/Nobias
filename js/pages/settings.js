import { api } from '../api.js';

export function settingsPage(nav) {
  const d = document.createElement('div');

  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Configure your LLM backend and audit defaults.</p>
    </div>

    <!-- LLM Backend -->
    <div class="settings-card anim-2">
      <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:20px;font-size:15px;font-weight:600;color:var(--c-text-1)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v6M12 17v6M5.64 5.64l4.24 4.24M14.12 14.12l4.24 4.24M1 12h6M17 12h6M5.64 18.36l4.24-4.24M14.12 9.88l4.24-4.24"/></svg>
        LLM Backend
      </h3>
      <div class="form-group">
        <label class="form-label">LLM Provider</label>
        <select class="input select" id="llm-provider">
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="groq">Groq</option>
          <option value="gemini">Google Gemini</option>
          <option value="ollama">Ollama (Local)</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Default Model</label>
        <select class="input select" id="llm-model">
          <option value="gpt-4o">GPT-4o</option>
          <option value="gpt-4-turbo">GPT-4 Turbo</option>
          <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
          <option value="llama-3.1-70b-versatile">Llama 3.1 70B (Groq)</option>
          <option value="gemini-2.0-flash">Gemini 2.0 Flash (Google)</option>
          <option value="gemini-1.5-pro">Gemini 1.5 Pro (Google)</option>
          <option value="gemini-1.5-flash">Gemini 1.5 Flash (Google)</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">API Key</label>
        <div style="display:flex;gap:10px">
          <div style="position:relative;flex:1">
            <input type="password" class="input" id="api-key" placeholder="sk-..." style="padding-right:40px">
            <button id="toggle-key" type="button" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:var(--c-text-4)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
          <button class="btn btn-secondary" id="test-btn" style="white-space:nowrap">Test Connection</button>
        </div>
      </div>
      <div id="connection-status" style="display:none;margin-top:12px;padding:10px 14px;border-radius:8px;font-size:13px;display:none;align-items:center;gap:8px"></div>
      <div id="ollama-group" class="form-group" style="display:none">
        <label class="form-label">Ollama URL</label>
        <input type="text" class="input" id="ollama-url" placeholder="http://localhost:11434">
      </div>
    </div>

    <!-- Audit Defaults -->
    <div class="settings-card anim-3">
      <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:20px;font-size:15px;font-weight:600;color:var(--c-text-1)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-teal)" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        Audit Defaults
      </h3>
      <div class="form-group">
        <label class="form-label">Default Audit Mode</label>
        <div class="segmented" id="audit-mode-seg">
          <button class="segmented-opt" data-mode="quick">? Quick</button>
          <button class="segmented-opt active" data-mode="standard">Standard</button>
          <button class="segmented-opt" data-mode="full">Full</button>
        </div>
      </div>
    </div>

    <!-- Danger zone -->
    <div class="settings-card anim-4" style="border-color:var(--c-critical-bdr)">
      <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:16px;font-size:15px;font-weight:600;color:var(--c-critical)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Danger Zone
      </h3>
      <p style="font-size:13px;color:var(--c-text-3);margin-bottom:16px">This will permanently delete all audit history. This action cannot be undone.</p>
      <button class="btn" id="clear-history-btn" style="background:var(--c-critical-bg);color:var(--c-critical);border:1px solid var(--c-critical-bdr)">
        Clear All History
      </button>
    </div>

    <!-- Toast -->
    <div id="toast" style="display:none;position:fixed;bottom:24px;right:24px;background:var(--c-clear-bg);border:1px solid var(--c-clear-bdr);color:var(--c-clear);padding:10px 18px;border-radius:8px;font-size:13px;font-weight:600;display:none;align-items:center;gap:8px;z-index:9999">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
      Settings saved
    </div>
  `;

  setTimeout(async () => {
    const toast         = d.querySelector('#toast');
    const connStatus    = d.querySelector('#connection-status');
    const ollamaGroup   = d.querySelector('#ollama-group');
    const providerSel   = d.querySelector('#llm-provider');
    const modelSel      = d.querySelector('#llm-model');
    const apiKeyInput   = d.querySelector('#api-key');
    const ollamaInput   = d.querySelector('#ollama-url');

    function showToast() {
      toast.style.display = 'flex';
      setTimeout(() => { toast.style.display = 'none'; }, 2000);
    }

    async function save(patch) {
      try {
        await api.settings.update(patch);
        showToast();
      } catch (err) {
        alert('Failed to save: ' + err.message);
      }
    }

    function toggleOllama() {
      ollamaGroup.style.display = providerSel.value === 'ollama' ? 'block' : 'none';
    }

    // -- Load settings -----------------------------------------------------
    try {
      const s = await api.settings.get();
      providerSel.value  = s.llm_provider || 'openai';
      modelSel.value     = s.llm_model    || 'gpt-4o';
      apiKeyInput.value  = s.api_key      ? '����������������' : '';
      ollamaInput.value  = s.ollama_url   || 'http://localhost:11434';
      toggleOllama();

      const activeMode = s.default_audit_mode || 'standard';
      d.querySelectorAll('#audit-mode-seg button').forEach(b => {
        b.classList.toggle('active', b.dataset.mode === activeMode);
      });
    } catch (err) {
      console.warn('Could not load settings:', err.message);
    }

    // -- Provider change ---------------------------------------------------
    providerSel.addEventListener('change', () => {
      toggleOllama();
      save({ llm_provider: providerSel.value });
    });

    modelSel.addEventListener('change', () => save({ llm_model: modelSel.value }));

    // -- API key -----------------------------------------------------------
    d.querySelector('#toggle-key').addEventListener('click', () => {
      apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
    });

    apiKeyInput.addEventListener('blur', () => {
      const val = apiKeyInput.value.trim();
      if (val && !val.includes('�')) save({ api_key: val });
    });

    ollamaInput.addEventListener('blur', () => {
      const val = ollamaInput.value.trim();
      if (val) save({ ollama_url: val });
    });

    // -- Audit mode --------------------------------------------------------
    d.querySelectorAll('#audit-mode-seg button').forEach(btn => {
      btn.addEventListener('click', () => {
        d.querySelectorAll('#audit-mode-seg button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        save({ default_audit_mode: btn.dataset.mode });
      });
    });

    // -- Test connection ---------------------------------------------------
    d.querySelector('#test-btn').addEventListener('click', async () => {
      const btn = d.querySelector('#test-btn');
      btn.textContent = 'Testing...';
      btn.disabled = true;
      connStatus.style.display = 'none';

      try {
        const result = await api.settings.testConnection();
        const ok = result.connected;
        connStatus.style.display = 'flex';
        connStatus.style.background   = ok ? 'var(--c-clear-bg)'    : 'var(--c-critical-bg)';
        connStatus.style.border       = `1px solid ${ok ? 'var(--c-clear-bdr)' : 'var(--c-critical-bdr)'}`;
        connStatus.style.color        = ok ? 'var(--c-clear)'        : 'var(--c-critical)';
        connStatus.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="${ok ? 'M20 6 9 17l-5-5' : 'M18 6 6 18M6 6l12 12'}"/>
          </svg>
          <span>${ok ? '? ' : '? '}${result.message || (ok ? 'Connected' : 'Connection failed')}</span>`;
      } catch (err) {
        connStatus.style.display = 'flex';
        connStatus.style.background = 'var(--c-critical-bg)';
        connStatus.style.border     = '1px solid var(--c-critical-bdr)';
        connStatus.style.color      = 'var(--c-critical)';
        connStatus.innerHTML = `<span>? Connection failed: ${err.message}</span>`;
      } finally {
        btn.textContent = 'Test Connection';
        btn.disabled = false;
      }
    });

    // -- Clear history -----------------------------------------------------
    d.querySelector('#clear-history-btn').addEventListener('click', async () => {
      const confirmed = window.confirm(
        'Delete ALL audit history?\n\nThis will permanently remove all saved audits and cannot be undone.'
      );
      if (!confirmed) return;
      try {
        await api.history.clear();
        alert('All history cleared.');
      } catch (err) {
        alert('Failed to clear history: ' + err.message);
      }
    });

  }, 0);

  return d;
}
