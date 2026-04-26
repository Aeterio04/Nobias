// ── Nobias App — Main Entry ──
import { renderSidebar } from './sidebar.js';
import { renderTopbar } from './topbar.js';
import { pages } from './pages/index.js';

const routes = {
  '':                 'welcome',
  'dashboard':        'dashboard',
  'dataset-upload':   'datasetUpload',
  'dataset-configure':'datasetConfigure',
  'dataset-running':  'datasetRunning',
  'dataset-results':  'datasetResults',
  'model-upload':     'modelUpload',
  'model-results':    'modelResults',
  'agent-setup':      'agentSetup',
  'agent-running':    'agentRunning',
  'agent-results':    'agentResults',
  'audit-comparison': 'auditComparison',
  'settings':         'settings',
  'documentation':    'documentation',
};

const pageTitles = {
  welcome:'Dashboard',dashboard:'Dashboard',
  datasetUpload:'Dataset Auditor',datasetConfigure:'Configure Your Dataset',
  datasetRunning:'Analysing Dataset',datasetResults:'Audit Results',
  modelUpload:'Model Auditor',modelResults:'Model Auditor',
  agentSetup:'Agent Auditor',agentRunning:'Audit Console',agentResults:'Agent Auditor',
  auditComparison:'Audit Comparison',settings:'Settings',documentation:'Documentation',
};

const pageBreadcrumbs = {
  datasetUpload:'Modules / Dataset Auditor',
  datasetConfigure:'Modules / Dataset Auditor',
  datasetRunning:'Modules / Dataset Auditor',
  datasetResults:'Modules / Dataset Auditor / Results',
  modelUpload:'Modules / Model Auditor',
  modelResults:'Modules / Model Auditor / Results',
  agentSetup:'Modules / Agent Auditor',
  agentRunning:'Modules / Agent Auditor',
  agentResults:'Modules / Agent Auditor / Results',
};

function getRoute() {
  return window.location.hash.replace('#/', '').replace('#', '') || '';
}

function navigate(route) {
  window.location.hash = '#/' + route;
}

function render() {
  const hash = getRoute();
  const pageKey = routes[hash] || 'welcome';
  const content = document.getElementById('page-content');
  const topbar = document.getElementById('topbar');
  
  // Render sidebar
  renderSidebar(document.getElementById('sidebar'), hash, navigate);
  
  // Render topbar
  renderTopbar(topbar, pageTitles[pageKey], pageBreadcrumbs[pageKey], navigate);
  
  // Render page
  if (pages[pageKey]) {
    content.innerHTML = '';
    const pageEl = pages[pageKey](navigate);
    if (typeof pageEl === 'string') {
      content.innerHTML = pageEl;
    } else {
      content.appendChild(pageEl);
    }
  }
}

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

// Expose navigate globally for onclick handlers
window.navigate = navigate;
