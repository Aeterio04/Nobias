// Simple state management
const state = {
  datasetUpload: null,
  datasetResult: null,
  datasetLoading: false,
  datasetError: null,
  
  modelUpload: null,
  testDataUpload: null,
  modelResult: null,
  modelLoading: false,
  modelError: null,
  compatibility: null,
  
  agentResult: null,
  agentLoading: false,
  agentError: null,
  agentProgress: 0,
  
  history: [],
  settings: null,
  apiConnected: false,
};

const listeners = [];

export function getState() {
  return state;
}

export function setState(updates) {
  Object.assign(state, updates);
  listeners.forEach(fn => fn(state));
}

export function subscribe(fn) {
  listeners.push(fn);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx > -1) listeners.splice(idx, 1);
  };
}

export function clearDatasetState() {
  setState({
    datasetUpload: null,
    datasetResult: null,
    datasetLoading: false,
    datasetError: null,
  });
}

export function clearModelState() {
  setState({
    modelUpload: null,
    testDataUpload: null,
    modelResult: null,
    modelLoading: false,
    modelError: null,
    compatibility: null,
  });
}

export function clearAgentState() {
  setState({
    agentResult: null,
    agentLoading: false,
    agentError: null,
    agentProgress: 0,
  });
}
