// ── Sidebar Component — Lucide SVG icons ──
const icons = {
  dashboard: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  dataset: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h18M3 12h18M3 19h18"/><path d="M9 5v14M15 5v14"/></svg>',
  model: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>',
  agent: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect x="5" y="8" width="14" height="12" rx="2"/><path d="M10 14h.01M14 14h.01"/></svg>',
  docs: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  settings: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
};

const navItems = [
  { section: 'MODULES' },
  { icon: 'dashboard', label: 'Dashboard', route: 'dashboard' },
  { icon: 'dataset', label: 'Dataset Auditor', route: 'dataset-upload' },
  { icon: 'model', label: 'Model Auditor', route: 'model-upload' },
  { icon: 'agent', label: 'Agent Auditor', route: 'agent-setup' },
  { section: 'HISTORY' },
  { dot: '#DC2626', label: 'Q3_Financial_D...', route: 'dataset-results' },
  { dot: '#D97706', label: 'Customer_Chur...', route: 'dataset-results' },
  { dot: '#059669', label: 'Support_Bot_Be...', route: 'agent-results' },
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
      if (item.dot) {
        return `<a href="#/${item.route}" class="history-item">
          <span class="history-dot" style="background:${item.dot}"></span>
          <span>${item.label}</span>
        </a>`;
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
      <div class="sidebar-status">
        <span class="status-dot"></span>
        <span>API Connected</span>
      </div>
      <a href="#/settings" class="nav-item${active === 'settings' ? ' active' : ''}">
        <span class="nav-icon">${icons.settings}</span><span>Settings</span>
      </a>
    </div>
  `;
}
