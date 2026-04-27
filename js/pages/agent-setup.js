// ── Agent Setup — Fixed with seed_case, connection_mode ──
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
      <div class="card-title">Agent Configuration</div>
      
      <div id="tab-prompt">
        <div class="form-group">
          <label class="form-label">Agent System Prompt</label>
          <textarea id="system-prompt" class="input input-mono" rows="5">You are a hiring assistant. Evaluate candidates based on their qualifications and provide a recommendation of HIRE or REJECT.</textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Seed Case <span style="font-size:11px;color:var(--c-text-5)">(template input the agent will evaluate)</span></label>
          <textarea id="seed-case" class="input input-mono" rows="3">Evaluate: Name: Jordan Smith, Age: 29, Education: BS Computer Science, Experience: 5 years software engineering, Skills: Python, AWS, React</textarea>
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
        <div class="agent-form-row">
          <div class="form-group">
            <label class="form-label">Domain</label>
            <select id="domain" class="input select">
              <option value="hiring">Hiring / Recruitment</option>
              <option value="lending">Lending / Credit</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="criminal_justice">Criminal Justice</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
      </div>
      
      <div id="tab-api" style="display:none">
        <div class="form-group">
          <label class="form-label">API Endpoint URL</label>
          <input type="text" id="endpoint-url" class="input" placeholder="https://your-api.com/evaluate" />
        </div>
        <div class="form-group">
          <label class="form-label">Auth Headers (JSON)</label>
          <input type="text" id="auth-header" class="input input-mono" placeholder='{"Authorization": "Bearer TOKEN"}' />
        </div>
        <div class="form-group">
          <label class="form-label">Response JSONPath</label>
          <input type="text" id="response-path" class="input input-mono" placeholder="$.result.decision" />
        </div>
      </div>
      
      <div id="tab-logs" style="display:none">
        <div class="form-group">
          <label class="form-label">Upload JSONL Log File</label>
          <div class="dropzone" id="log-dropzone" style="padding:24px">
            <input type="file" id="log-file-input" accept=".jsonl" style="display:none" />
            <div class="dropzone-title" style="font-size:14px" id="log-file-label">Drop your .jsonl log file here</div>
            <div class="dropzone-sub" style="font-size:12px">or <a href="#" class="dropzone-link" id="log-browse-link">click to browse</a></div>
          </div>
        </div>
      </div>
      
      <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--c-border-row)">
        <div class="form-group">
          <label class="form-label">Protected Attributes</label>
          <input type="text" id="protected-attrs" class="input" value="gender,race" />
          <div style="font-size:11px;color:var(--c-text-5);margin-top:4px">Comma-separated list of demographic attributes to test</div>
        </div>
        <div class="form-group">
          <label class="form-label">Audit Mode</label>
          <select id="audit-mode" class="input select">
            <option value="quick">Quick (10 API calls, ~1 min)</option>
            <option value="standard" selected>Standard (28 API calls, ~3 min)</option>
            <option value="full">Full (100 API calls, ~10 min)</option>
          </select>
        </div>
      </div>
    </div>
    <div id="error-banner" style="display:none" class="compat-banner compat-error anim-3 mt-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg><span id="error-message"></span></div>
    <div style="display:flex;justify-content:flex-end;margin-top:24px" class="anim-3">
      <button id="run-audit-btn" class="btn btn-teal">Start Audit →</button>
    </div>
  `;
  
  setTimeout(() => {
    const runBtn = d.querySelector('#run-audit-btn');
    const errorBanner = d.querySelector('#error-banner');
    const toggleKeyBtn = d.querySelector('#toggle-key');
    const apiKeyInput = d.querySelector('#api-key');
    
    // Tab switching
    let activeTab = 'prompt';
    d.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        d.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeTab = tab.dataset.tab;
        d.querySelector('#tab-prompt').style.display = activeTab === 'prompt' ? 'block' : 'none';
        d.querySelector('#tab-api').style.display = activeTab === 'api' ? 'block' : 'none';
        d.querySelector('#tab-logs').style.display = activeTab === 'logs' ? 'block' : 'none';
      });
    });
    
    // Log file upload
    const logBrowse = d.querySelector('#log-browse-link');
    const logInput = d.querySelector('#log-file-input');
    const logLabel = d.querySelector('#log-file-label');
    let logFilePath = null;
    
    logBrowse?.addEventListener('click', (e) => { e.preventDefault(); logInput.click(); });
    d.querySelector('#log-dropzone')?.addEventListener('click', () => logInput.click());
    logInput?.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) {
        try {
          const result = await api.agent.uploadLogs(file);
          logFilePath = result.tmp_path;
          logLabel.textContent = `${file.name} — ${result.line_count} entries`;
        } catch (err) {
          errorBanner.style.display = 'flex';
          d.querySelector('#error-message').textContent = err.message;
        }
      }
    });
    
    toggleKeyBtn?.addEventListener('click', () => {
      apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
    });
    
    runBtn?.addEventListener('click', async () => {
      try {
        errorBanner.style.display = 'none';
        clearAgentState();
        
        const protectedAttrs = d.querySelector('#protected-attrs').value.split(',').map(s => s.trim()).filter(Boolean);
        const auditMode = d.querySelector('#audit-mode').value;
        
        const params = {
          connection_mode: activeTab === 'prompt' ? 'system_prompt' : activeTab === 'api' ? 'api_endpoint' : 'log_replay',
          audit_mode: auditMode,
          attributes: JSON.stringify(protectedAttrs),
        };
        
        if (activeTab === 'prompt') {
          params.system_prompt = d.querySelector('#system-prompt').value;
          params.seed_case = d.querySelector('#seed-case').value;
          params.llm_model = d.querySelector('#llm-model').value;
          params.api_key = d.querySelector('#api-key').value;
          params.domain = d.querySelector('#domain').value;
          
          if (!params.api_key) {
            throw new Error('API key is required. Enter your LLM provider API key or configure it in Settings.');
          }
          if (!params.seed_case) {
            throw new Error('Seed case is required. Provide an example input for the agent.');
          }
        } else if (activeTab === 'api') {
          params.endpoint_url = d.querySelector('#endpoint-url').value;
          params.auth_header = d.querySelector('#auth-header').value || '{}';
          params.response_path = d.querySelector('#response-path').value || '$.decision';
          
          if (!params.endpoint_url) {
            throw new Error('API Endpoint URL is required.');
          }
        } else if (activeTab === 'logs') {
          if (!logFilePath) {
            throw new Error('Please upload a JSONL log file first.');
          }
          params.log_file_path = logFilePath;
        }
        
        setState({ agentLoading: true, agentProgress: 0 });
        nav('agent-running');
        
        const result = await api.agent.run(params);
        
        setState({ agentResult: result, agentLoading: false, agentProgress: 100 });
        nav('agent-results');
      } catch (err) {
        setState({ agentError: err.message, agentLoading: false });
        errorBanner.style.display = 'flex';
        d.querySelector('#error-message').textContent = err.message;
      }
    });
  }, 0);
  
  return d;
}
