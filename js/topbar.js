// ── Top Bar — Redesigned ──
const bellIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>';
const clockIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>';
const searchIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>';

export function renderTopbar(el, title, breadcrumb, navigate) {
  el.innerHTML = `
    <div class="topbar-left">
      ${breadcrumb ? `<span class="topbar-breadcrumb">${breadcrumb}</span>` : `<span class="topbar-title">${title || 'Dashboard'}</span>`}
    </div>
    <div class="topbar-right">
      <div class="topbar-search">${searchIcon} Search audits...</div>
      <button class="btn btn-primary btn-sm" onclick="navigate('dataset-upload')">Run Audit</button>
      <button class="topbar-icon-btn" title="Notifications">${bellIcon}</button>
      <button class="topbar-icon-btn" title="History">${clockIcon}</button>
      <div class="topbar-avatar" title="User profile">SV</div>
    </div>
  `;
}
