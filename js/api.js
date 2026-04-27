const BASE = "http://127.0.0.1:8000/api";

async function request(method, path, body, isFormData = false) {
  const opts = { method };
  if (body) {
    if (isFormData) {
      opts.body = body;
    } else {
      opts.headers = { "Content-Type": "application/json" };
      opts.body = JSON.stringify(body);
    }
  }
  
  let res;
  try {
    res = await fetch(`${BASE}${path}`, opts);
  } catch (err) {
    throw new Error("Cannot connect to the Nobias backend. Make sure the Python server is running: cd backend && python main.py");
  }
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  
  return res.json();
}

export const api = {
  health: () => request("GET", "/health"),
  
  dataset: {
    upload: (file) => {
      const fd = new FormData();
      fd.append("file", file);
      return request("POST", "/dataset/upload", fd, true);
    },
    run: (params) => {
      const fd = new FormData();
      fd.append("tmp_path", params.tmp_path);
      fd.append("protected_attributes", JSON.stringify(params.protected_attributes));
      fd.append("target_column", params.target_column);
      fd.append("positive_value", String(params.positive_value));
      fd.append("audit_mode", params.audit_mode || "standard");
      return request("POST", "/dataset/run", fd, true);
    },
    samples: () => request("GET", "/dataset/samples"),
    loadSample: (sampleId) => request("POST", `/dataset/load-sample/${sampleId}`),
    export: (auditId, format = 'json') => request("GET", `/dataset/export/${auditId}?format=${format}`),
  },
  
  model: {
    uploadModel: (file) => {
      const fd = new FormData();
      fd.append("file", file);
      return request("POST", "/model/upload-model", fd, true);
    },
    uploadTestData: (file) => {
      const fd = new FormData();
      fd.append("file", file);
      return request("POST", "/model/upload-testdata", fd, true);
    },
    checkCompatibility: (model_path, testdata_path) => {
      const fd = new FormData();
      fd.append("model_path", model_path);
      fd.append("testdata_path", testdata_path);
      return request("POST", "/model/check-compatibility", fd, true);
    },
    run: (params) => {
      const fd = new FormData();
      fd.append("model_path", params.model_path);
      fd.append("testdata_path", params.testdata_path);
      fd.append("protected_attributes", JSON.stringify(params.protected_attributes));
      fd.append("target_column", params.target_column);
      fd.append("positive_value", String(params.positive_value));
      return request("POST", "/model/run", fd, true);
    },
    export: (auditId, format = 'json') => request("GET", `/model/export/${auditId}?format=${format}`),
  },
  
  agent: {
    run: (params) => {
      const fd = new FormData();
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) {
          fd.append(k, typeof v === 'object' ? JSON.stringify(v) : String(v));
        }
      });
      return request("POST", "/agent/run", fd, true);
    },
    uploadLogs: (file) => {
      const fd = new FormData();
      fd.append("file", file);
      return request("POST", "/agent/upload-logs", fd, true);
    },
    compare: (before_id, after_id) => {
      const fd = new FormData();
      fd.append("audit_id_before", before_id);
      fd.append("audit_id_after", after_id);
      return request("POST", "/agent/compare", fd, true);
    },
    export: (auditId, format = 'json') => request("GET", `/agent/export/${auditId}?format=${format}`),
  },
  
  history: {
    list: () => request("GET", "/history/"),
    get: (id) => request("GET", `/history/${id}`),
    delete: (id) => request("DELETE", `/history/${id}`),
    clear: () => request("DELETE", "/history/"),
  },
  
  settings: {
    get: () => request("GET", "/settings/"),
    update: (s) => request("POST", "/settings/", s),
    testConnection: () => request("POST", "/settings/test-connection"),
  },
};
