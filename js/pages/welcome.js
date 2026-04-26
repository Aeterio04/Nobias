// ── Welcome Page — Redesigned ──
export function welcomePage(nav) {
  const d = document.createElement('div');
  d.className = 'anim-1';
  d.innerHTML = `
    <div class="welcome-hero">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--c-text-5)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
      <h1 class="page-title" style="margin-top:24px">Welcome to Nobias</h1>
      <p style="font-size:14px;color:var(--c-text-3);max-width:480px;margin:8px auto 0">Select a module to begin analyzing your datasets, models, or agents for bias and compliance issues.</p>
      <div class="welcome-modules">
        <div class="welcome-module" onclick="navigate('dataset-upload')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="1.5"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg>
          <span>Dataset</span>
        </div>
        <div class="welcome-module" onclick="navigate('model-upload')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-violet)" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg>
          <span>Model</span>
        </div>
        <div class="welcome-module" onclick="navigate('agent-setup')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent-teal)" stroke-width="1.5"><path d="M12 8V4H8"/><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M10 14h.01M14 14h.01"/></svg>
          <span>Agent</span>
        </div>
      </div>
    </div>
  `;
  return d;
}
