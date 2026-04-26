// ── Agent Setup — Redesigned ──
export function agentSetupPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1">
      <h1 class="page-title" style="display:flex;align-items:center;gap:12px">Agent Auditor <span class="badge badge-teal" style="font-size:11px">MOST POWERFUL</span></h1>
      <p class="page-subtitle">Test your LLM agent for demographic bias using synthetic persona testing.</p>
    </div>
    <div class="anim-2"><div class="tabs"><button class="tab active">System Prompt</button><button class="tab">API Endpoint</button><button class="tab">Log Replay</button></div></div>
    <div class="card anim-2">
      <div class="card-title">Agent Setup</div>
      <div class="form-group">
        <label class="form-label">Agent System Prompt</label>
        <textarea class="input input-mono" rows="5">You are a hiring assistant. Evaluate candidates based on their qualifications and provide a recommendation of HIRE or REJECT.</textarea>
      </div>
      <div class="agent-form-row">
        <div class="form-group"><label class="form-label">LLM Model</label><select class="input select"><option>OpenAI GPT-4o</option><option>Anthropic Claude 3.5</option><option>Meta Llama 3</option><option>Ollama (Local)</option></select></div>
        <div class="form-group"><label class="form-label">API Key</label><div class="api-key-input"><input type="password" class="input" value="sk-••••••••••••••••••••" /><button class="api-key-toggle"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg></button></div></div>
      </div>
    </div>
    <div style="display:flex;justify-content:flex-end;margin-top:24px" class="anim-3">
      <button class="btn btn-teal" onclick="navigate('agent-running')">Run Agent Audit →</button>
    </div>
  `;
  return d;
}
