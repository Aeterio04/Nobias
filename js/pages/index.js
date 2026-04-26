// ── Pages Index ──
import { welcomePage } from './welcome.js';
import { dashboardPage } from './dashboard.js';
import { datasetUploadPage } from './dataset-upload.js';
import { datasetConfigurePage } from './dataset-configure.js';
import { datasetRunningPage } from './dataset-running.js';
import { datasetResultsPage } from './dataset-results.js';
import { modelUploadPage } from './model-upload.js';
import { modelResultsPage } from './model-results.js';
import { agentSetupPage } from './agent-setup.js';
import { agentRunningPage } from './agent-running.js';
import { agentResultsPage } from './agent-results.js';
import { auditComparisonPage } from './audit-comparison.js';
import { settingsPage } from './settings.js';
import { documentationPage } from './documentation.js';

export const pages = {
  welcome: welcomePage,
  dashboard: dashboardPage,
  datasetUpload: datasetUploadPage,
  datasetConfigure: datasetConfigurePage,
  datasetRunning: datasetRunningPage,
  datasetResults: datasetResultsPage,
  modelUpload: modelUploadPage,
  modelResults: modelResultsPage,
  agentSetup: agentSetupPage,
  agentRunning: agentRunningPage,
  agentResults: agentResultsPage,
  auditComparison: auditComparisonPage,
  settings: settingsPage,
  documentation: documentationPage,
};
