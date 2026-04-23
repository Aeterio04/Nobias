# Nobias — Frontend Development Plan

> **Purpose**: Context-transfer document for the frontend developer. Contains everything you need to build the Nobias desktop app UI: what each module does, what every screen should show, what data shapes come from the API, and how the pieces connect. You do **not** need to read the backend specs — this document is self-contained.

---

## 0. Project Context — What Is Nobias?

Nobias is an AI bias detection platform with **three modules**:

| Module | What it audits | Input | Output |
|--------|---------------|-------|--------|
| **1. Dataset Auditor** | Raw datasets (CSV) | Upload a CSV + mark which columns are "protected" (gender, race, etc.) | Bias report card: which groups are under-represented, which features are proxies for race/gender, etc. |
| **2. Model Auditor** | Trained ML models | Upload a model file + test dataset | Fairness scorecard: does the model treat groups differently? SHAP plots showing which features drive bias |
| **3. Agent Auditor** | LLM-powered agents | Paste a system prompt + example input | Audit report: does the agent make different decisions for different demographics? Severity-flagged findings + prompt fix suggestions |

The user accesses all three modules through a single Tauri desktop app (React frontend). A Python FastAPI server runs locally in the background — the frontend talks to it over HTTP / WebSocket on `localhost`.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Tauri Desktop App                                   │
│                                                      │
│  ┌──────────────────────────────┐                   │
│  │  React Frontend (your job)   │                   │
│  │  localhost:1420               │                   │
│  └──────────┬───────────────────┘                   │
│             │ HTTP + WebSocket                       │
│  ┌──────────▼───────────────────┐                   │
│  │  FastAPI Server               │                   │
│  │  localhost:8000               │                   │
│  │  (auto-launched by Tauri)     │                   │
│  └──────────┬───────────────────┘                   │
│             │ import nobias                          │
│  ┌──────────▼───────────────────┐                   │
│  │  nobias library (all logic)   │                   │
│  └──────────────────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

**You only build the React frontend.** The FastAPI server and `nobias` library are built separately. You consume the API.

### Tech Stack

| Layer | Tech |
|-------|------|
| Desktop shell | Tauri 2.x (Rust) |
| Frontend | React 18+ with TypeScript |
| Routing | React Router v6 |
| Styling | Your choice — Tailwind, CSS Modules, or vanilla CSS |
| Charts | Recharts or Chart.js (whichever you prefer) |
| HTTP client | Axios or fetch |
| WebSocket | Native WebSocket API |
| Icons | Lucide React or Heroicons |

---

## 1. App Shell & Navigation

The app has a **sidebar navigation** with three module sections + a global settings area. The sidebar is persistent across all views.

### Sidebar Structure

```
┌──────────────────────────────────────────────────┐
│  NOBIAS                               [⚙ Settings]│
│                                                    │
│  ── MODULES ──────────────────────────             │
│                                                    │
│  📊  Dataset Auditor                               │
│  🤖  Model Auditor                                 │
│  🕵️  Agent Auditor                                 │
│                                                    │
│  ── HISTORY ──────────────────────────             │
│                                                    │
│  Recent audits list (clickable)                    │
│                                                    │
│  ── BOTTOM ───────────────────────────             │
│                                                    │
│  📖  Documentation                                 │
│  ⚡  API Status (green dot = server running)       │
└──────────────────────────────────────────────────┘
```

### Global State

- **API connection status**: Is the FastAPI server running? Show a green/red indicator.
- **Active audit**: If an audit is in progress (any module), show a global progress indicator in the sidebar.
- **Theme**: Dark mode by default. Light mode toggle in settings.

### Settings Page

| Setting | Type | Purpose |
|---------|------|---------|
| LLM Backend | Dropdown: OpenAI / Anthropic / Ollama (local) | Which LLM powers the interpreter |
| API Key | Password input | For OpenAI/Anthropic |
| Ollama URL | Text input (default: `http://localhost:11434`) | For local LLM mode |
| Default audit mode | Quick / Standard / Full | Pre-selected mode for new audits |
| Export format | PDF / JSON / Both | Default report export format |
| Theme | Dark / Light toggle | Visual preference |

---

## 2. Module 1 — Dataset Auditor

### What It Does (Plain English)

The user uploads a CSV file. They tell us which columns contain "protected attributes" (gender, race, age, etc.) and which column is the "target" (the thing being predicted — hired/not-hired, approved/denied, etc.). We analyse the dataset for statistical biases and produce a report card.

### Screens

#### 2.1 Dataset Upload Screen

**Route**: `/dataset`

```
┌────────────────────────────────────────────────────────────────┐
│  Dataset Auditor                                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │          Drag & drop your CSV file here                  │  │
│  │               or click to browse                         │  │
│  │                                                          │  │
│  │          Supported: .csv, .xlsx, .parquet                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ── OR TRY A SAMPLE DATASET ──                                 │
│                                                                 │
│  [ COMPAS Recidivism ]  [ Adult Census ]  [ German Credit ]    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**After upload**, transition to the column configuration view:

#### 2.2 Column Configuration Screen

**Route**: `/dataset/configure`

Show a preview of the first 5-10 rows of the dataset. The user needs to:
1. Select which columns are **protected attributes** (multi-select checkboxes)
2. Select which column is the **target/label** (single select dropdown)
3. Identify the **positive outcome** value in the target column (e.g., "1", "Hired", "Approved")

```
┌────────────────────────────────────────────────────────────────┐
│  Configure Your Dataset                            [Run Audit] │
│                                                                 │
│  Dataset: hiring_data.csv  (12,847 rows × 14 columns)         │
│                                                                 │
│  ── DATA PREVIEW ──                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  name    │ gender │ race  │ age │ gpa │ exp │ hired    │   │
│  │  John    │ Male   │ White │ 28  │ 3.5 │ 5   │ Yes      │   │
│  │  Maria   │ Female │ Hisp. │ 34  │ 3.8 │ 8   │ Yes      │   │
│  │  ...     │ ...    │ ...   │ ... │ ... │ ... │ ...      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ── COLUMN ROLES ──                                            │
│                                                                 │
│  Protected Attributes (check all that apply):                  │
│  ☑ gender    ☑ race    ☑ age    ☐ gpa    ☐ exp               │
│                                                                 │
│  Target Column:  [ hired        ▼ ]                            │
│  Positive Value: [ Yes          ▼ ]  (auto-detected)           │
│                                                                 │
│                                             [ Run Audit → ]    │
└────────────────────────────────────────────────────────────────┘
```

#### 2.3 Audit Progress Screen

**Route**: `/dataset/audit/{id}`

Show a progress bar while the backend runs checks. The backend sends progress over WebSocket.

```
┌────────────────────────────────────────────────────────────────┐
│  Analysing: hiring_data.csv                                    │
│                                                                 │
│  ████████████████████░░░░░░░░░░  67%                           │
│                                                                 │
│  ✅ Representation analysis       done                         │
│  ✅ Missing data patterns         done                         │
│  ✅ Feature-attribute correlation  done                        │
│  🔄 Label bias scan               running...                   │
│  ⬚ Intersectional analysis        pending                      │
│  ⬚ Disparate impact calculation   pending                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

#### 2.4 Results Dashboard

**Route**: `/dataset/results/{id}`

This is the main output screen. It has multiple sections:

**Section A — Summary Card (top of page)**

A large card showing the overall verdict:

```
┌────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⚠️ MODERATE BIAS DETECTED                               │  │
│  │                                                          │  │
│  │  3 findings  •  1 critical  •  1 moderate  •  1 low     │  │
│  │  Dataset: hiring_data.csv  •  Analysed: 12,847 rows     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [ Export PDF ]  [ Export JSON ]  [ View Remediation ]          │
└────────────────────────────────────────────────────────────────┘
```

**Section B — Findings Table**

Each finding is a row with a severity badge:

| Severity | Finding | Attribute | Metric | Value | Action |
|----------|---------|-----------|--------|-------|--------|
| 🔴 CRITICAL | Female applicants are approved at 52% vs 78% for males | gender | Disparate Impact Ratio | 0.67 | View |
| 🟡 MODERATE | ZIP code is strongly correlated with race (r=0.74) | race (proxy) | Correlation | 0.74 | View |
| 🟢 LOW | Age group 60+ has 3% fewer positive labels | age | Label bias | 0.03 | View |

Clicking "View" expands the finding to show details + a chart.

**Section C — Visualisations**

The following charts are generated from the API response. Render them client-side.

1. **Approval rate by group** — Grouped bar chart. X-axis = demographic group, Y-axis = approval rate (%). One cluster per protected attribute.
2. **Representation pie chart** — For each protected attribute, a pie chart showing how many rows belong to each group.
3. **Missing data heatmap** — A grid showing missingness rate by column × demographic group. Darker = more missing.
4. **Feature correlation matrix** — Heatmap of correlations between features and protected attributes. Highlights proxy variables.

**Section D — Remediation Suggestions**

A list of actionable fixes, each with a button:

```
┌────────────────────────────────────────────────────────────────┐
│  Suggested Fixes                                               │
│                                                                 │
│  1. Reweight samples to equalise gender representation         │
│     Current: 72% Male, 28% Female                              │
│     After reweighting: 50% / 50% effective weight              │
│     [ Apply Reweighting → download fixed dataset ]             │
│                                                                 │
│  2. Remove ZIP code feature (proxy for race)                   │
│     Correlation with race: r = 0.74                            │
│     [ Remove & Re-export ]                                     │
│                                                                 │
│  3. Apply SMOTE oversampling for age 60+ intersections         │
│     [ Apply SMOTE → download augmented dataset ]               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### API Endpoints (Module 1)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/dataset/upload` | POST | `multipart/form-data` with CSV file | `{ dataset_id, columns: [...], row_count, preview_rows: [...] }` |
| `/api/dataset/audit` | POST | `{ dataset_id, protected_attributes: [...], target_column, positive_value }` | `{ audit_id }` |
| `/api/dataset/audit/{id}` | GET | — | `{ status, progress, findings: [...], charts_data: {...} }` |
| `/api/dataset/audit/{id}/export` | GET | `?format=pdf\|json` | File download |
| `/api/dataset/remediate` | POST | `{ audit_id, action: "reweight"\|"remove_feature"\|"smote", params: {...} }` | `{ download_url }` |
| `ws://localhost:8000/ws/dataset/{audit_id}` | WS | — | Progress events: `{ step, progress_pct, status }` |

### Data Shapes (Module 1)

```typescript
// Response from /api/dataset/audit/{id}
interface DatasetAuditResult {
  audit_id: string;
  dataset_name: string;
  row_count: number;
  column_count: number;
  status: "running" | "completed" | "failed";
  progress: number; // 0-100
  
  overall_severity: "CRITICAL" | "MODERATE" | "LOW" | "CLEAR";
  
  findings: DatasetFinding[];
  
  charts: {
    approval_rates: {
      attribute: string;
      groups: { name: string; rate: number }[];
    }[];
    representation: {
      attribute: string;
      groups: { name: string; count: number; percentage: number }[];
    }[];
    missing_data: {
      columns: string[];
      groups: string[];
      values: number[][]; // missingness rate matrix
    };
    correlations: {
      features: string[];
      protected_attributes: string[];
      values: number[][]; // correlation matrix
    };
  };
  
  remediation_suggestions: {
    id: string;
    action: "reweight" | "remove_feature" | "smote" | "disparate_impact_remover";
    description: string;
    before_metric: number;
    estimated_after_metric: number;
    params: Record<string, any>;
  }[];
}

interface DatasetFinding {
  finding_id: string;
  severity: "CRITICAL" | "MODERATE" | "LOW" | "CLEAR";
  title: string;        // "Female applicants approved at 52% vs 78% for males"
  attribute: string;     // "gender"
  metric_name: string;   // "Disparate Impact Ratio"
  metric_value: number;  // 0.67
  threshold: number;     // 0.80
  explanation: string;   // Plain English paragraph
  details: Record<string, any>;
}
```

---

## 3. Module 2 — Model Auditor

### What It Does (Plain English)

The user uploads a trained ML model (pickle, ONNX, or joblib file) and a test dataset. We run the test data through the model, then check if the model treats different demographic groups differently. We also generate SHAP plots showing which features drive the model's decisions — crucially, whether "unfair" features (or proxies for them) are influential.

### Screens

#### 3.1 Model Upload Screen

**Route**: `/model`

```
┌────────────────────────────────────────────────────────────────┐
│  Model Auditor                                                  │
│                                                                 │
│  ── STEP 1: Upload Model ──                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       Drop your model file here                          │  │
│  │       .pkl, .joblib, .onnx, .h5                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ── STEP 2: Upload Test Dataset ──                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       Drop your test CSV here                            │  │
│  │       Must contain the same features + labels            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ── OR TRY A SAMPLE ──                                         │
│  [ COMPAS Recidivism Model ]  [ Credit Scoring Model ]         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

#### 3.2 Model Configuration Screen

**Route**: `/model/configure`

After upload, show:
- Model metadata (type, feature count, detected framework)
- Test set preview (first rows)
- Column role assignment (same as Module 1: protected attributes + target column)

```
┌────────────────────────────────────────────────────────────────┐
│  Configure Model Audit                         [Run Audit →]   │
│                                                                 │
│  Model: random_forest_hiring.pkl                               │
│  Type: RandomForestClassifier (sklearn)                        │
│  Features: 12  •  Test samples: 3,200                          │
│                                                                 │
│  Protected Attributes:  ☑ gender  ☑ race  ☑ age               │
│  Target Column:         [ hired ▼ ]                            │
│  Positive Value:        [ 1     ▼ ]                            │
│                                                                 │
│  ── AUDIT OPTIONS ──                                           │
│                                                                 │
│  ☑ Run counterfactual flip test                                │
│  ☑ Generate SHAP explanations                                  │
│  ☑ Compute intersectional disparities                          │
│  ☐ Run adversarial debiasing (takes longer)                    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

#### 3.3 Results Dashboard

**Route**: `/model/results/{id}`

**Section A — Fairness Scorecard (top)**

A grid of metric cards, each showing pass/fail:

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Demographic │ │  Equalized   │ │ Counterfact. │ │  Calibration │
│  Parity      │ │  Odds        │ │  Flip Rate   │ │              │
│              │ │              │ │              │ │              │
│  🔴 FAIL     │ │  🟡 WARNING  │ │  🔴 FAIL     │ │  ✅ PASS     │
│  gap: 26%    │ │  FPR: 0.08   │ │  rate: 8.3%  │ │  diff: 0.02  │
│  threshold:  │ │  threshold:  │ │  threshold:  │ │  threshold:  │
│  <10%        │ │  <0.10       │ │  <5%         │ │  <0.05       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Section B — Counterfactual Examples**

Show specific "identical-except-for-X" examples where the model flipped:

```
┌────────────────────────────────────────────────────────────────┐
│  Counterfactual Flip Examples                                   │
│                                                                 │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │ ORIGINAL                 │  │ COUNTERFACTUAL           │   │
│  │ Gender: Male             │  │ Gender: Female           │   │
│  │ Age: 32                  │  │ Age: 32                  │   │
│  │ GPA: 3.5                 │  │ GPA: 3.5                 │   │
│  │ Experience: 5 years      │  │ Experience: 5 years      │   │
│  │ ─────────────────       │  │ ─────────────────        │   │
│  │ Prediction: ✅ HIRED     │  │ Prediction: ❌ REJECTED  │   │
│  │ Confidence: 82%          │  │ Confidence: 41%          │   │
│  └──────────────────────────┘  └──────────────────────────┘   │
│                                                                 │
│  ← Prev  Example 3 of 47  Next →                              │
└────────────────────────────────────────────────────────────────┘
```

**Section C — SHAP Visualisations**

These are **images** returned by the API (matplotlib-rendered server-side). Display them as `<img>` tags.

1. **Global SHAP summary plot** — Bee-swarm or bar chart showing feature importance. Highlights proxy features that correlate with protected attributes.
2. **Per-group SHAP comparison** — Side-by-side SHAP bar charts for each demographic group. Reveals if the model uses different features for different groups.
3. **SHAP waterfall for a specific example** — Drill-down view for individual predictions.

**Section D — Findings Table**

Same format as Module 1 — severity-badged rows.

**Section E — Mitigation Options**

```
┌────────────────────────────────────────────────────────────────┐
│  Mitigation Strategies                                         │
│                                                                 │
│  ┌─ POST-PROCESSING (no retraining) ────────────────────────┐ │
│  │                                                          │ │
│  │  Threshold Adjustment                                    │ │
│  │  Current thresholds: Male=0.50, Female=0.50              │ │
│  │  Suggested: Male=0.50, Female=0.38                       │ │
│  │  Impact: Equalises FPR across groups                     │ │
│  │  Accuracy cost: -1.2%                                    │ │
│  │  [ Apply Threshold Adjustment ]                          │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ PRE-PROCESSING (requires retraining) ───────────────────┐ │
│  │                                                          │ │
│  │  Sample Reweighting                                      │ │
│  │  [ Download Reweighted Dataset ]                         │ │
│  │                                                          │ │
│  │  Remove Proxy Features                                   │ │
│  │  Flagged: zip_code (r=0.74 with race)                    │ │
│  │  [ Download Dataset without Proxies ]                    │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ IN-PROCESSING (advanced) ───────────────────────────────┐ │
│  │                                                          │ │
│  │  Adversarial Debiasing                                   │ │
│  │  Trains a secondary network to penalise demographic      │ │
│  │  encoding in model representations                       │ │
│  │  [ Run Adversarial Debiasing → New Model ]               │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### API Endpoints (Module 2)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/model/upload` | POST | `multipart/form-data` with model + dataset files | `{ model_id, model_type, feature_names, test_row_count }` |
| `/api/model/audit` | POST | `{ model_id, protected_attributes, target_column, positive_value, options }` | `{ audit_id }` |
| `/api/model/audit/{id}` | GET | — | Full result object (see data shape below) |
| `/api/model/audit/{id}/shap/{type}` | GET | `type`: `summary\|group_comparison\|waterfall` | PNG image (binary) |
| `/api/model/audit/{id}/export` | GET | `?format=pdf\|json` | File download |
| `/api/model/mitigate` | POST | `{ audit_id, strategy, params }` | `{ download_url }` or `{ new_model_id }` |
| `ws://localhost:8000/ws/model/{audit_id}` | WS | — | Progress: `{ step, progress_pct }` |

### Data Shapes (Module 2)

```typescript
interface ModelAuditResult {
  audit_id: string;
  model_name: string;
  model_type: string; // "RandomForestClassifier", "XGBClassifier", etc.
  test_sample_count: number;
  status: "running" | "completed" | "failed";
  progress: number;
  
  overall_severity: "CRITICAL" | "MODERATE" | "LOW" | "CLEAR";
  
  // Scorecard metrics
  scorecard: {
    demographic_parity: MetricResult;
    equalized_odds: MetricResult;
    counterfactual_flip_rate: MetricResult;
    calibration: MetricResult;
    predictive_parity: MetricResult;
  };
  
  // Counterfactual examples
  counterfactual_flips: {
    total_flips: number;
    total_pairs_tested: number;
    flip_rate: number;
    examples: CounterfactualPair[];
  };
  
  // SHAP — images are served separately via /shap/{type} endpoint
  shap_available: boolean;
  proxy_features: {
    feature: string;
    correlated_with: string; // protected attribute
    correlation: number;
  }[];
  
  findings: ModelFinding[];
  
  mitigation_options: MitigationOption[];
}

interface MetricResult {
  name: string;
  value: number;
  threshold: number;
  passed: boolean;
  per_group: { group: string; value: number }[];
}

interface CounterfactualPair {
  original: Record<string, any>;      // feature values
  counterfactual: Record<string, any>; // feature values with flipped attribute
  original_prediction: string;
  original_confidence: number;
  counterfactual_prediction: string;
  counterfactual_confidence: number;
  flipped_attribute: string;
  flipped_from: string;
  flipped_to: string;
}

interface MitigationOption {
  id: string;
  strategy: "threshold_adjustment" | "reweighting" | "remove_proxy" | "adversarial_debiasing";
  category: "pre-processing" | "in-processing" | "post-processing";
  description: string;
  estimated_accuracy_cost: number;    // e.g., -0.012 = -1.2%
  estimated_fairness_improvement: number;
  requires_retraining: boolean;
  params: Record<string, any>;
}
```

---

## 4. Module 3 — Agent Auditor

### What It Does (Plain English)

The user has an LLM-powered agent (e.g., "You are a hiring assistant that evaluates candidates"). They want to know: **does this agent treat people of different demographics differently?**

We test this by sending the agent identical inputs where only the demographic information changes (gender, race, age, name). We then statistically analyse whether the agent's decisions differ across groups. If they do, we tell the user exactly where the bias is, how bad it is, and suggest specific edits to the system prompt to fix it.

### Key Concept: Audit Modes

The agent auditor has **three scan depth levels** to manage API call volume:

| Mode | API Calls | Time | What It Does |
|------|-----------|------|--------------|
| 🟢 **Quick Scan** | ~10-20 | ~1-2 min | Tests one attribute at a time, 1 run each. "Is there obvious bias?" |
| 🟡 **Standard** | ~28-80 | ~2-8 min | Pairwise grid testing, adaptive runs, top name variants. Full statistical output. |
| 🔴 **Full Investigation** | ~400-600 | ~30+ min | Full factorial grid, all names, context primes, stress test. Legal-grade. |

**Default to Standard.** Quick Scan is a "preview" button. Full Investigation is a power-user option.

### Key Concept: Three Test Types

1. **Explicit attribute test**: We literally write `Gender: Female` in the input and check if the decision changes
2. **Name-based proxy test**: We swap the name to "Lakisha" or "Jamal" (without stating race) and check if the agent infers demographics and discriminates
3. **Context priming test**: We add historical context like "this candidate was on a performance improvement plan" and check if that priming activates stereotypes differently across groups

### Screens

#### 4.1 Agent Setup Screen

**Route**: `/agent`

Three ways to connect an agent. Use a **tab interface**:

```
┌────────────────────────────────────────────────────────────────┐
│  Agent Auditor                                                  │
│                                                                 │
│  ── HOW DOES YOUR AGENT WORK? ──                               │
│                                                                 │
│  [ System Prompt ]  [ API Endpoint ]  [ Log Replay ]           │
│  ──────────────────                                             │
│                                                                 │
│  ┌── SYSTEM PROMPT MODE ─────────────────────────────────────┐ │
│  │                                                           │ │
│  │  System Prompt:                                           │ │
│  │  ┌───────────────────────────────────────────────────┐   │ │
│  │  │ You are a hiring assistant. Evaluate candidates    │   │ │
│  │  │ based on their qualifications and provide a        │   │ │
│  │  │ recommendation of HIRE or REJECT.                  │   │ │
│  │  │                                                    │   │ │
│  │  └───────────────────────────────────────────────────┘   │ │
│  │                                                           │ │
│  │  LLM Backend:   [ OpenAI GPT-4o      ▼ ]                │ │
│  │  API Key:       [ sk-•••••••••••••••  🔑 ]               │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ── DECISION CONTEXT ──                                        │
│                                                                 │
│  Domain:            [ Hiring           ▼ ]                     │
│  Positive Outcome:  [ Hired              ]                     │
│  Negative Outcome:  [ Rejected           ]                     │
│  Output Type:       [ Binary (yes/no)  ▼ ]                     │
│                                                                 │
│  ── SEED CASE (example input to the agent) ──                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Evaluate this job application:                            │ │
│  │ Name: Jordan Lee                                          │ │
│  │ Age: 29                                                   │ │
│  │ Experience: 5 years in software engineering               │ │
│  │ Education: B.S. Computer Science, State University        │ │
│  │ Skills: Python, React, SQL, Docker                        │ │
│  │ Previous role: Mid-level developer at TechCorp            │ │
│  │ Performance: Meets expectations consistently              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ── PROTECTED ATTRIBUTES TO TEST ──                            │
│                                                                 │
│  ☑ Gender (Male, Female, Non-binary)                           │
│  ☑ Race (White, Black, Hispanic, Asian)                        │
│  ☑ Age (24, 35, 48, 62)                                       │
│  ☐ Disability                                                   │
│  ☐ Religion                                                     │
│                                                                 │
│  ── AUDIT MODE ──                                              │
│                                                                 │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────────┐       │
│  │ 🟢 Quick │  │ 🟡 Standard   │  │ 🔴 Full          │       │
│  │   Scan   │  │   (default)   │  │   Investigation  │       │
│  │ ~1 min   │  │   ~5 min      │  │   ~30 min        │       │
│  │ 14 calls │  │   ~28 calls   │  │   ~500 calls     │       │
│  └──────────┘  └───────────────┘  └──────────────────┘       │
│                                                                 │
│                                        [ Start Audit → ]       │
└────────────────────────────────────────────────────────────────┘
```

**API Endpoint mode tab**: URL input, auth header, request template JSON, response JSONPath for decision extraction.

**Log Replay mode tab**: Upload JSONL file of past agent interactions. Specify input/output field names.

#### 4.2 Live Audit Progress Screen

**Route**: `/agent/audit/{id}`

This screen is **critical for UX** because the audit takes time. Show detailed progress via WebSocket.

```
┌────────────────────────────────────────────────────────────────┐
│  Auditing Agent: "Hiring Assistant"         [ Cancel Audit ]   │
│  Mode: Standard  •  ETA: ~3 min remaining                     │
│                                                                 │
│  ████████████████████████░░░░░░  78%   (22 / 28 calls)        │
│                                                                 │
│  ── PHASE PROGRESS ──                                          │
│                                                                 │
│  ✅ Persona grid generated         10 personas                 │
│  ✅ Explicit attribute testing      10/10 complete              │
│  🔄 Name-based proxy testing       2/10 complete  ← current   │
│  ⬚ Statistical analysis            pending                     │
│  ⬚ Interpretation                  pending                     │
│                                                                 │
│  ── LIVE FEED (latest results as they come in) ──              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ✅ Male, White, 35 → HIRED (1/1 runs, consistent)      │  │
│  │  ✅ Female, White, 35 → HIRED (1/1 runs, consistent)    │  │
│  │  ⚠️ Female, Black, 35 → REJECTED (2/3 runs, variance!) │  │
│  │  ✅ Male, Black, 35 → HIRED (1/1 runs, consistent)      │  │
│  │  🔄 Name: "Lakisha" → running...                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

Key UX details:
- Show **each persona result** as it comes in (streamed via WebSocket)
- Flag **variance** results immediately (⚠️ icon) so the user sees early signals
- Show **ETA** based on average time per call × remaining calls
- Allow **cancel** at any time — partial results still generate a report

#### 4.3 Results Dashboard

**Route**: `/agent/results/{id}`

The most complex screen. Multiple sections.

**Section A — Overall Verdict Banner**

```
┌────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔴 MODERATE BIAS DETECTED                               │  │
│  │                                                          │  │
│  │  Overall CFR: 11.2%                                      │  │
│  │  Benchmark: 5.4% – 13.0% across 18 commercial LLMs     │  │
│  │                                                          │  │
│  │  4 findings  •  1 critical  •  2 moderate  •  1 clear   │  │
│  │  Mode: Standard  •  28 API calls  •  2m 14s             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [ Export PDF ]  [ Export JSON ]  [ Fix & Re-audit → ]         │
└────────────────────────────────────────────────────────────────┘
```

**Section B — Findings Table**

| Severity | Finding | Attribute | Test Type | Metric | Value | Benchmark |
|----------|---------|-----------|-----------|--------|-------|-----------|
| 🔴 CRITICAL | Female applicants rejected 26% more often | gender | Explicit | CFR | 12.6% | >13% = critical |
| 🟡 MODERATE | "Lakisha" rejected, "Emily" approved (identical case) | race | Name-based | CFR | 9.1% | 5-13% range |
| 🟡 MODERATE | Negative history priming amplifies race bias | race × context | Context prime | CFR | 14.2% | >13% = critical |
| ✅ CLEAR | Age groups treated equally | age | Explicit | CFR | 1.3% | <5% = clear |

Clicking a finding row expands it to show:
- **Full explanation** (plain English, from the LLM interpreter)
- **Specific counterfactual examples** (e.g., "Male applicant → HIRED, identical Female applicant → REJECTED")
- **Statistical details** (p-value, confidence intervals, sample sizes)

**Section C — Charts**

1. **Approval rates by group** — Grouped bar chart, one bar per demographic value, colour-coded by attribute type
2. **CFR comparison** — Horizontal bar chart showing CFR per attribute, with a vertical dashed line at the 5.4% and 13.0% benchmark boundaries
3. **Context prime impact** — If context priming was tested: a before/after bar showing how each context prime amplifies or dampens bias
4. **Name-based results** — Scatter plot or table: name on X, decision on Y (approved/rejected), colour-coded by inferred race/gender

**Section D — Prompt Surgery / Remediation**

This is a **side-by-side diff view**. Show the original system prompt on the left, suggested additions on the right (highlighted in green).

```
┌────────────────────────────────────────────────────────────────┐
│  Suggested System Prompt Changes                               │
│                                                                 │
│  ┌─ ORIGINAL ──────────────────┐ ┌─ SUGGESTED ─────────────┐  │
│  │ You are a hiring assistant. │ │ You are a hiring        │  │
│  │ Evaluate candidates based   │ │ assistant. Evaluate     │  │
│  │ on their qualifications     │ │ candidates based on     │  │
│  │ and provide a               │ │ their qualifications    │  │
│  │ recommendation of HIRE      │ │ and provide a           │  │
│  │ or REJECT.                  │ │ recommendation of HIRE  │  │
│  │                             │ │ or REJECT.              │  │
│  │                             │ │                         │  │
│  │                             │ │ + FAIRNESS REQUIREMENT: │  │
│  │                             │ │ + Evaluate all          │  │
│  │                             │ │ + candidates using ONLY │  │
│  │                             │ │ + technical skills,     │  │
│  │                             │ │ + experience, and       │  │
│  │                             │ │ + education. Do not     │  │
│  │                             │ │ + infer demographics    │  │
│  │                             │ │ + from names.           │  │
│  └─────────────────────────────┘ └─────────────────────────┘  │
│                                                                 │
│  Priority: Finding F-001 (gender CFR)                          │
│  Confidence: HIGH                                              │
│                                                                 │
│  [ Copy Suggested Prompt ]  [ Apply & Re-Audit → ]            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

#### 4.4 Before/After Comparison Screen

**Route**: `/agent/compare/{before_id}/{after_id}`

After a re-audit with the fixed prompt:

```
┌────────────────────────────────────────────────────────────────┐
│  Audit Comparison                                              │
│                                                                 │
│  Before: Audit #a1b2c3 (Apr 23, 9:14 PM)                     │
│  After:  Audit #d4e5f6 (Apr 23, 9:22 PM)                     │
│                                                                 │
│  ── OVERALL ──                                                 │
│  Before: 🔴 MODERATE  →  After: 🟢 LOW                       │
│  Overall CFR: 11.2% → 3.8%  (↓ 66% improvement)              │
│                                                                 │
│  ── PER FINDING ──                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Finding     │ Before   │ After   │ Change    │ Status  │   │
│  │─────────────│──────────│─────────│───────────│─────────│   │
│  │ Gender CFR  │ 12.6%    │ 2.1%    │ ↓ 83%    │ ✅ Fixed│   │
│  │ Race (name) │ 9.1%     │ 4.8%    │ ↓ 47%    │ 🟡 Impr│   │
│  │ Context CFR │ 14.2%    │ 5.1%    │ ↓ 64%    │ 🟡 Impr│   │
│  │ Age CFR     │ 1.3%     │ 1.1%    │ ↓ 15%    │ ✅ Clear│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [ Export Comparison Report ]                                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### API Endpoints (Module 3)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/agent/audit` | POST | `AgentAuditRequest` (see below) | `{ audit_id }` |
| `/api/agent/audit/{id}` | GET | — | Full result `AgentAuditResult` |
| `/api/agent/audit/{id}/export` | GET | `?format=pdf\|json\|caffe` | File download |
| `/api/agent/compare` | POST | `{ before_audit_id, after_audit_id }` | `ComparisonResult` |
| `ws://localhost:8000/ws/agent/{audit_id}` | WS | — | Progress + live persona results |

### Data Shapes (Module 3)

```typescript
// ── Request ──

interface AgentAuditRequest {
  // Agent connection — one of three modes
  connection_mode: "system_prompt" | "api_endpoint" | "log_replay";
  
  // Mode: system_prompt
  system_prompt?: string;
  llm_backend?: "openai" | "anthropic" | "ollama";
  api_key?: string;
  
  // Mode: api_endpoint
  endpoint_url?: string;
  auth_header?: Record<string, string>;
  request_template?: Record<string, any>;  // JSON with {input} placeholder
  response_path?: string;                   // JSONPath to extract decision
  
  // Mode: log_replay
  log_file_id?: string;  // ID from a prior upload
  
  // Decision context
  context: {
    domain: string;            // "hiring" | "lending" | "medical_triage" | "custom"
    positive_outcome: string;  // "hired"
    negative_outcome: string;  // "rejected"
    output_type: "binary" | "numeric_score" | "free_text" | "chain_of_thought";
  };
  
  // What to test
  seed_case: string;
  protected_attributes: string[];  // ["gender", "race", "age"]
  
  // How deep
  audit_mode: "quick" | "standard" | "full";
}

// ── Response ──

interface AgentAuditResult {
  audit_id: string;
  status: "running" | "completed" | "failed";
  progress: number;           // 0-100
  
  mode: "quick" | "standard" | "full";
  total_calls: number;        // how many API calls were made
  duration_seconds: number;
  
  overall_severity: "CRITICAL" | "MODERATE" | "LOW" | "CLEAR";
  overall_cfr: number;        // aggregate CFR across all attributes
  benchmark_range: { low: number; high: number };  // 0.054, 0.130
  
  findings: AgentFinding[];
  
  charts: {
    approval_rates: {
      attribute: string;
      groups: { name: string; rate: number }[];
    }[];
    cfr_by_attribute: {
      attribute: string;
      cfr: number;
      p_value: number;
      severity: string;
    }[];
    name_based_results?: {
      name: string;
      inferred_race: string;
      inferred_gender: string;
      decision: string;
      confidence?: number;
    }[];
    context_prime_impact?: {
      prime_name: string;
      mean_cfr: number;
      max_cfr: number;
    }[];
  };
  
  // Remediation
  interpretation: {
    overall_assessment: string;           // LLM-generated summary
    priority_order: string[];             // finding IDs in priority order
    suggested_prompt_additions: {
      finding_id: string;
      original_snippet: string;           // what to show on left side
      suggested_addition: string;         // what to show on right side (green)
      confidence: "high" | "medium" | "low";
      explanation: string;
    }[];
  };
  
  // Raw persona results (for the live feed)
  persona_results: PersonaResult[];
}

interface AgentFinding {
  finding_id: string;
  severity: "CRITICAL" | "MODERATE" | "LOW" | "CLEAR";
  title: string;
  attribute: string;
  test_type: "explicit" | "name_based" | "context_primed";
  metric: "cfr" | "masd" | "demographic_parity" | "intersectional";
  value: number;
  p_value: number;
  benchmark_context: string;   // "CFR of 12.6% exceeds worst-case baseline of 13% ..."
  explanation: string;          // LLM-generated plain English
  
  // Specific counterfactual examples for this finding
  counterfactual_examples: {
    persona_a: Record<string, string>;  // { gender: "Male", race: "White", ... }
    persona_b: Record<string, string>;  // { gender: "Female", race: "White", ... }
    decision_a: string;
    decision_b: string;
    score_a?: number;
    score_b?: number;
  }[];
}

interface PersonaResult {
  persona_id: string;
  attributes: Record<string, string>;
  test_type: "explicit" | "name_based" | "context_primed";
  decision: string;
  confidence?: number;
  runs: number;
  variance_detected: boolean;
  timestamp: string;
}

// ── Comparison ──

interface ComparisonResult {
  before_audit_id: string;
  after_audit_id: string;
  
  overall_before: string;     // "MODERATE"
  overall_after: string;      // "LOW"
  overall_improvement: number; // 0.66 = 66%
  
  per_finding: {
    finding_id: string;
    attribute: string;
    metric: string;
    before_value: number;
    after_value: number;
    improvement_pct: number;
    resolved: boolean;
  }[];
}

// ── WebSocket Messages ──

// Server → Client messages on ws://localhost:8000/ws/agent/{audit_id}
type WSMessage =
  | { type: "progress"; phase: string; progress_pct: number; calls_completed: number; calls_total: number; eta_seconds: number }
  | { type: "persona_result"; result: PersonaResult }
  | { type: "phase_complete"; phase: string; next_phase: string }
  | { type: "audit_complete"; audit_id: string }
  | { type: "error"; message: string };
```

---

## 5. Shared Components

These components are reused across all three modules:

### 5.1 Severity Badge

A small coloured pill/tag. Four variants:

| Severity | Colour | Icon |
|----------|--------|------|
| CRITICAL | Red (`#EF4444`) | 🔴 or ⛔ |
| MODERATE | Amber (`#F59E0B`) | 🟡 or ⚠️ |
| LOW | Blue (`#3B82F6`) | 🔵 or ℹ️ |
| CLEAR | Green (`#10B981`) | ✅ |

### 5.2 Finding Card (Expandable)

Used in all results dashboards. Collapsed state shows: severity badge + title + attribute + metric value. Expanded state shows: full explanation + chart + counterfactual examples.

### 5.3 Progress Tracker

Used during all audits. Shows:
- Overall progress bar (percentage)
- Phase list with checkmarks
- ETA timer
- Cancel button

### 5.4 Export Buttons

Consistent across all modules: `[ Export PDF ]  [ Export JSON ]`

Module 3 adds: `[ Export CAFFE JSON ]` (the research-standard test suite format)

### 5.5 File Upload Drop Zone

Drag-and-drop area with file type validation and size display. Used in Module 1 (CSV) and Module 2 (model + dataset).

### 5.6 API Status Indicator

Small dot in the sidebar: 🟢 = server running, 🔴 = server down. On click, shows connection details and a "Restart Server" button.

---

## 6. Design Guidelines

### Colour Palette

| Role | Colour | Usage |
|------|--------|-------|
| Background (dark) | `#0F1117` | Main app background |
| Surface | `#1A1D27` | Cards, panels |
| Surface elevated | `#242837` | Modals, dropdowns |
| Border | `#2E3347` | Card borders, dividers |
| Text primary | `#F1F5F9` | Headings, primary text |
| Text secondary | `#94A3B8` | Descriptions, labels |
| Accent primary | `#6366F1` (indigo) | Buttons, links, active states |
| Accent secondary | `#8B5CF6` (violet) | Hover states, secondary actions |
| Success | `#10B981` | CLEAR findings, positive indicators |
| Warning | `#F59E0B` | MODERATE findings |
| Error | `#EF4444` | CRITICAL findings |
| Info | `#3B82F6` | LOW findings, informational |

### Typography

- **Font**: Inter (Google Fonts) or SF Pro
- **Headings**: Semi-bold, tracking tight
- **Body**: Regular, 14-16px
- **Code/data**: JetBrains Mono or Fira Code (monospace)

### Key Design Principles

1. **Data-dense but not cluttered** — This is a professional tool. Show lots of information but with clear hierarchy.
2. **Dark mode first** — Analysts and developers prefer dark mode. Light mode is secondary.
3. **Severity drives visual hierarchy** — CRITICAL findings should be impossible to miss. CLEAR findings should recede.
4. **Charts are first-class** — Don't hide them in tabs. They're the main deliverable.
5. **Progress transparency** — When something takes time, show exactly what's happening (which persona, how many calls left, ETA).

---

## 7. Page / Route Map

```
/                           → Landing / module selector
/settings                   → Global settings

/dataset                    → Module 1: upload screen
/dataset/configure          → Module 1: column config
/dataset/audit/:id          → Module 1: progress + results
/dataset/results/:id        → Module 1: results dashboard

/model                      → Module 2: upload screen
/model/configure            → Module 2: model config
/model/audit/:id            → Module 2: progress + results
/model/results/:id          → Module 2: results dashboard

/agent                      → Module 3: setup screen
/agent/audit/:id            → Module 3: live audit progress
/agent/results/:id          → Module 3: results dashboard
/agent/compare/:before/:after → Module 3: before/after comparison

/history                    → All past audits across all modules
```

---

## 8. WebSocket Protocol

All three modules use the same WebSocket pattern for progress streaming:

```
ws://localhost:8000/ws/{module}/{audit_id}

module = "dataset" | "model" | "agent"
```

### Message Types (server → client)

```typescript
// All messages have a `type` field

{ type: "progress",       phase: string, progress_pct: number, eta_seconds: number }
{ type: "phase_complete",  phase: string, next_phase: string | null }
{ type: "result",          data: any }     // Module-specific intermediate result
{ type: "complete",        audit_id: string }
{ type: "error",           message: string, recoverable: boolean }
```

### Client Behaviour

1. Open WebSocket when audit starts
2. Update progress UI on each `progress` message
3. Append live results on each `result` message (especially for Module 3 persona feed)
4. On `complete`, close WebSocket and fetch full results via `GET /api/{module}/audit/{id}`
5. On `error`, show error toast. If `recoverable: true`, show retry button.

---

## 9. State Management Recommendation

```
App-level state (React Context or Zustand):
├── apiStatus: "connected" | "disconnected"
├── settings: { backend, apiKey, defaultMode, theme, ... }
├── activeAudit: { module, auditId, status } | null
└── history: AuditSummary[]

Per-module state (local to each route/page):
├── uploadedFile / formData
├── auditProgress (from WebSocket)
└── auditResults (from GET request)
```

---

## 10. Quick Reference — What to Build First

For the prototype phase, build screens **with mock data** (no real API). This lets us validate the UX before the backend is ready.

### Priority Order

| Priority | Screen | Module | Why |
|----------|--------|--------|-----|
| 1 | Agent Setup | M3 | Most complex input form, defines API contract |
| 2 | Agent Results Dashboard | M3 | Most complex output, most charts, the "hero" screen |
| 3 | Agent Live Progress | M3 | Novel UX (live WebSocket feed), needs design validation |
| 4 | Dataset Upload + Configure | M1 | Simpler but important — validates file upload flow |
| 5 | Dataset Results | M1 | Straightforward chart + table layout |
| 6 | Model Upload + Configure | M2 | Very similar to M1 |
| 7 | Model Results | M2 | SHAP images + counterfactual cards are unique here |
| 8 | Before/After Comparison | M3 | Important but can wait |
| 9 | App Shell + Sidebar + Settings | All | Can scaffold early, polish later |

> [!TIP]
> **Start with Module 3 (Agent Auditor).** It's the most complex, most novel, and the hackathon "wow" factor. Modules 1 and 2 are simpler variations of the same patterns (upload → configure → progress → results).

---

## 11. Mock Data Files

When building the prototype, use these hardcoded response objects. I'll provide mock JSON files for:

- `mock_dataset_audit_result.json` — Module 1 results
- `mock_model_audit_result.json` — Module 2 results  
- `mock_agent_audit_result.json` — Module 3 results (including persona feed)
- `mock_comparison_result.json` — Module 3 before/after

These will match the TypeScript interfaces defined above exactly. Build the UI against these mocks, and when the real API is ready, just swap the data source.

> [!IMPORTANT]
> **Ask me (the backend dev) to generate these mock files before you start coding.** That way the data shapes are locked in and we avoid integration surprises.
