import { api } from './api.js';
import { setState } from './store.js';

const icons = {
  dashboard: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  dataset: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg>`,
  model: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg>`,
  agent: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 8V4H8"/><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M10 14h.01M14 14h.01"/></svg>`,
  docs: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>`,
  settings: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v6M12 17v6M5.64 5.64l4.24 4.24M14.12 14.12l4.24 4.24M1 12h6M17 12h6M5.64 18.36l4.24-4.24M14.12 9.88l4.24-4.24"/></svg>`,
};

const navItems = [
  { section: 'MODULES' },
  { icon: 'dashboard', label: 'Dashboard', route: 'dashboard' },
  { icon: 'dataset', label: 'Dataset Auditor', route: 'dataset-upload' },
  { icon: 'model', label: 'Model Auditor', route: 'model-upload' },
  { icon: 'agent', label: 'Agent Auditor', route: 'agent-setup' },
];

export function renderSidebar(el, currentRoute, navigate) {
  const activeRoutes = {
    '': 'dashboard', 'dashboard': 'dashboard',
    'dataset-upload': 'dataset-upload', 'dataset-configure': 'dataset-upload',
    'dataset-running': 'dataset-upload', 'dataset-results': 'dataset-upload',
    'model-upload': 'model-upload', 'model-results': 'model-upload',
    'agent-setup': 'agent-setup', 'agent-running': 'agent-setup', 'agent-results': 'agent-setup',
    'audit-comparison': 'audit-comparison', 'settings': 'settings', 'documentation': 'documentation',
  };
  const active = activeRoutes[currentRoute] || 'dashboard';

  el.innerHTML = `
    <div class="sidebar-logo">
      <h1>NOBIAS</h1>
      <span>AI Trust Engine</span>
    </div>
    <div class="sidebar-logo-sep"></div>
    ${navItems.map(item => {
      if (item.section) {
        return `<div class="sidebar-section"><div class="sidebar-section-label">${item.section}</div></div>`;
      }
      const isActive = active === item.route;
      return `<a href="#/${item.route}" class="nav-item${isActive ? ' active' : ''}">
        <span class="nav-icon">${icons[item.icon]}</span>
        <span>${item.label}</span>
      </a>`;
    }).join('')}
    <div class="sidebar-bottom">
      <a href="#/documentation" class="nav-item${active === 'documentation' ? ' active' : ''}">
        <span class="nav-icon">${icons.docs}</span><span>Documentation</span>
      </a>
      <div class="sidebar-status" id="api-status">
        <span class="status-dot" id="status-dot"></span>
        <span id="status-text">Checking...</span>
      </div>
      <a href="#/settings" class="nav-item${active === 'settings' ? ' active' : ''}">
        <span class="nav-icon">${icons.settings}</span><span>Settings</span>
      </a>
    </div>
  `;
  
  checkAPIHealth();
}

async function checkAPIHealth() {
  try {
    await api.health();
    const dot = document.querySelector('#status-dot');
    const text = document.querySelector('#status-text');
    if (dot && text) {
      dot.style.background = 'var(--c-clear)';
      text.textContent = 'API Connected';
      setState({ apiConnected: true });
    }
  } catch (err) {
    const dot = document.querySelector('#status-dot');
    const text = document.querySelector('#status-text');
    if (dot && text) {
      dot.style.background = 'var(--c-critical)';
      text.textContent = 'API Offline';
      setState({ apiConnected: false });
    }
  }
}

setInterval(checkAPIHealth, 30000);
