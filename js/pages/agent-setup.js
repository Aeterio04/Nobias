// ── Agent Setup — Redesigned ──
import { api } from '../api.js';
import { getState, setState, clearAgentState } from '../store.js';

export function agentSetupPage(nav) {
  const d = document.createElement('div');
  const state = getState();
  
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title" style="display:flex;align-items:center;gap:12px">Agent Auditor <span class="badge badge-teal" style="font-size:11px">MOST POWERFUL</span></h1>
      <p class="page-subtitle">Test your LLM agent for demographic bias using synthetic persona testing.</p>
    </div>
    <div class="anim-2"><div class="tabs"><button class="tab active" data-tab="prompt">System Prompt</button><button class="tab" data-tab="api">API Endpoint</button><button class="tab" data-tab="logs">Log Replay</button></div></div>
    <div class="card anim-2">
      <div class="card-title">Agent Setup</div>
      <div class="form-group">
        <label class="form-label">Agent System Prompt</label>
        <textarea id="system-prompt" class="input input-mono" rows="5">You are a hiring assistant. Evaluate candidates based on their qualifications and provide a recommendation of HIRE or REJECT.</textarea>
      </div>
      <div class="agent-form-row">
        <div class="form-group">
          <label class="form-label">LLM Model</label>
          <select id="llm-model" class="input select">
            <option value="gpt-4o">OpenAI GPT-4o</option>
            <option value="claude-3.5">Anthropic Claude 3.5</option>
            <option value="llama-3">Meta Llama 3</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">API Key</label>
          <div class="api-key-input">
            <input type="password" id="api-key" class="input" value="" placeholder="sk-..." />
            <button class="api-key-toggle" id="toggle-key"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg></button>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Protected Attributes (comma-separated)</label>
        <input type="text" id="protected-attrs" class="input" value="gender,race,age" />
      </div>
      <div class="form-group">
        <label class="form-label">Audit Mode</label>
        <select id="audit-mode" class="input select">
          <option value="standard">Standard (28 API calls, ~3 min)</option>
          <option value="comprehensive">Comprehensive (100 API calls, ~10 min)</option>
          <option value="quick">Quick (10 API calls, ~1 min)</option>
        </select>
      </div>
    </div>
    <div id="error-banner" style="display:none" class="compat-banner compat-error anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg><span id="error-message"></span></div>
    <div style="display:flex;justify-content:flex-end;margin-top:24px" class="anim-3">
      <button id="run-audit-btn" class="btn btn-teal">Run Agent Audit →</button>
    </div>
  `;
  
  setTimeout(() => {
    const runBtn = d.querySelector('#run-audit-btn');
    const errorBanner = d.querySelector('#error-banner');
    const toggleKeyBtn = d.querySelector('#toggle-key');
    const apiKeyInput = d.querySelector('#api-key');
    
    toggleKeyBtn?.addEventListener('click', () => {
      apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
    });
    
    runBtn?.addEventListener('click', async () => {
      try {
        errorBanner.style.display = 'none';
        clearAgentState();
        
        const systemPrompt = d.querySelector('#system-prompt').value;
        const llmModel = d.querySelector('#llm-model').value;
        const apiKey = d.querySelector('#api-key').value;
        const protectedAttrs = d.querySelector('#protected-attrs').value.split(',').map(s => s.trim());
        const auditMode = d.querySelector('#audit-mode').value;
        
        if (!apiKey) {
          throw new Error('API key is required');
        }
        
        setState({ agentLoading: true, agentProgress: 0 });
        nav('agent-running');
        
        const result = await api.agent.run({
          system_prompt: systemPrompt,
          llm_model: llmModel,
          api_key: apiKey,
          protected_attributes: protectedAttrs,
          audit_mode: auditMode
        });
        
        setState({ agentResult: result, agentLoading: false, agentProgress: 100 });
        nav('agent-results');
      } catch (err) {
        setState({ agentError: err.message, agentLoading: false });
        errorBanner.style.display = 'flex';
        d.querySelector('#error-message').textContent = `Agent audit failed: ${err.message}`;
      }
    });
  }, 0);
  
  return d;
}
