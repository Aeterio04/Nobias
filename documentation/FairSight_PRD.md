# FAIRSIGHT
## AI Bias Detection & Fairness Auditing Platform
**Product Requirements Document | v1.0**
Hackathon Submission · April 2025
*Confidential — Internal Use Only*

---

## Table of Contents

1. Executive Summary
2. Problem Statement
3. Solution Overview
4. Module 1 — Dataset Auditor
   - 4.1 Objectives & Scope
   - 4.2 Bias Types Detected
   - 4.3 Detection Pipeline
   - 4.4 Fairness Metrics
   - 4.5 Remediation Outputs
5. Module 2 — ML Model Auditor
   - 5.1 Objectives & Scope
   - 5.2 Real-World Motivation (COMPAS)
   - 5.3 Core Detection Techniques
   - 5.4 Explainability with SHAP
   - 5.5 Three-Stage Bias Pipeline
   - 5.6 Mitigation Strategies
6. Module 3 — Agent Auditor
   - 6.1 Objectives & Scope
   - 6.2 Five-Layer Architecture
   - 6.3 Persona Grid Generation
   - 6.4 Statistical Detection Engine
   - 6.5 LLM Interpreter & Remediation
   - 6.6 Research-Backed Enrichments
7. Technical Architecture
8. References

---

## 1. Executive Summary

FairSight is a locally-installed Windows desktop application that provides organisations, developers, and researchers with a systematic, evidence-based toolkit for detecting and remediating bias across three distinct layers of modern automated decision systems: raw datasets, trained ML models, and LLM-powered agents.

Algorithmic bias is no longer a theoretical concern. The ProPublica COMPAS study (2016) demonstrated that a recidivism prediction model used in US courts classified Black defendants as high-risk at nearly twice the rate of white defendants with similar profiles. Amazon's scrapped AI hiring tool down-ranked resumes containing the word 'women's'. Facial recognition systems from major vendors have been shown to misidentify darker-skinned individuals at error rates up to 34% higher than lighter-skinned counterparts. These are not edge cases — they are the documented, measurable consequences of deploying unaudited automated systems at scale.

FairSight attacks this problem at every stage of the ML pipeline — before training, after training, and at inference time — through three purpose-built modules. Each module is grounded in peer-reviewed fairness research and produces actionable, human-readable reports that go beyond flagging problems to suggest concrete fixes.

**Key Differentiators**

- Hybrid detection: statistics-first, LLM-as-interpreter. No hallucinated bias findings.
- Covers the full lifecycle: dataset -> model -> agent.
- Local-first: all processing on the user's machine. No data leaves the device by default.
- Intersectional analysis: detects compounded bias across multiple protected attributes simultaneously.
- Counterfactual testing: produces human-readable 'identical-except-for-race' evidence.
- Verify loop: re-run the same audit after applying a suggested fix to measure improvement.

---

## 2. Problem Statement

Computer programs now make life-changing decisions about who gets a job, a bank loan, medical treatment, or even criminal sentencing. When these programs learn from flawed or historically discriminatory data, they do not merely repeat those mistakes — they amplify them at machine speed and global scale.

Two distinct categories of automated decision system are in widespread production use today:

- **Pure ML systems** — statistical models trained on numeric or vectorised data that emit a score, label, or decision (e.g. credit scoring, resume screening, medical triage).
- **Agentic LLM systems** — systems with a system prompt, retrieval context, tool access, and multi-step reasoning that produce recommendations or decisions in natural language (e.g. AI hiring assistants, automated customer support resolution, risk advisory chatbots).

Existing bias-detection tools suffer from three critical gaps: (1) they operate on datasets or models in isolation, never the full pipeline; (2) they produce numerical reports that non-technical stakeholders cannot interpret or act on; and (3) none address the emerging class of LLM-based agents, which introduces entirely new bias mechanisms such as name-based proxy discrimination, tone-based differential reasoning, and system-prompt-encoded stereotypes.

---

## 3. Solution Overview

FairSight is structured as three independent but interoperable modules delivered through a single Tauri-based Windows desktop application. A Python backend runs locally as a subprocess, handling all statistical computation and optional LLM calls. All user data stays on-device by default.

| Module | Input | Core Method | Output |
|---|---|---|---|
| 1. Dataset Auditor | Raw CSV / DataFrame | EDA + statistical disparity analysis (aif360) | Bias report card + suggested pre-processing fixes |
| 2. ML Model Auditor | Trained model + test set | Counterfactual flip test + SHAP feature attribution | Fairness scorecard + SHAP plots + mitigation options |
| 3. Agent Auditor | System prompt or API endpoint | Persona grid + statistical disparity testing | Severity-flagged audit report + revised system prompt |

---

## 4. Module 1 — Dataset Auditor

### 4.1 Objectives & Scope

The Dataset Auditor is the first line of defence. A biased dataset will always produce a biased model regardless of algorithmic choices made downstream. As Pagano et al. (2023) note in their systematic review of 45 ML fairness papers, the majority of identified biases can be traced back to the data collection and labelling phase. This module makes those biases visible before a single model is trained.

The module accepts any tabular dataset (CSV, Excel, Parquet), asks the user to identify protected attribute columns (gender, race, age, nationality, etc.), and runs a comprehensive bias scan that produces a colour-coded report card.

### 4.2 Bias Types Detected

- **Representation Bias** — Certain groups are under-represented relative to the real population, meaning the model will see fewer examples to learn from and will generalise poorly for those groups.
- **Measurement Bias** — Features are measured with different accuracy or reliability for different groups (e.g., proxy variables like ZIP code that encode race).
- **Label Bias** — Historical human labelling decisions embedded in the target variable are themselves discriminatory.
- **Aggregation Bias** — Treating all demographic groups as a single population when subgroup behaviour differs substantially.
- **Intersectional Bias** — Compounded under-representation at the intersection of two protected attributes (e.g., Black women under-represented more than Black or women individually).

### 4.3 Detection Pipeline & Checks

The following checks are run automatically once a dataset and protected attribute columns are provided:

| Check | What It Detects | Library |
|---|---|---|
| Class imbalance per protected group | Under-representation of minority groups in positive labels | pandas, aif360 |
| Disparate impact ratio | Approval/positive rate < 80% of majority group (US EEOC legal threshold) | aif360 |
| Feature-attribute correlation | Proxy discrimination via ZIP code, occupation, neighbourhood, etc. | seaborn, pandas |
| Missing data distribution | Differential data missingness by group, leading to biased imputation | missingno |
| Label bias scan | Negative labels concentrated in one demographic | custom |
| Representation ratio | Ratio of each protected group in the training set vs population baseline | pandas, scipy |
| Intersectional analysis | Compounded under-representation at multiple attribute intersections | aif360, custom |

### 4.4 Key Fairness Metrics

The module computes the following core statistical measures, all of which have formal definitions in the fairness literature (Mehrabi et al., 2021; Pessach & Shmueli, 2022):

- **Statistical Parity Difference (SPD):** P(Y=1|A=unprivileged) - P(Y=1|A=privileged). A value of 0 means perfect parity. Values below -0.1 are flagged.
- **Disparate Impact Ratio (DIR):** P(Y=1|A=unprivileged) / P(Y=1|A=privileged). The US EEOC '80% rule' states a ratio below 0.8 constitutes adverse impact.
- **Normalised Mutual Information:** Measures the dependence between a feature and the protected attribute, surfacing proxy variables.
- **KL Divergence:** Measures the distribution shift of the target label across demographic subgroups.

### 4.5 Remediation Outputs

- **Reweighting (pre-processing):** Assigns higher sample weights to under-represented groups so the model treats them as equally important during training (Kamiran & Calders, 2012).
- **Disparate Impact Remover:** Edits feature values of non-protected attributes to improve group fairness while preserving rank-ordering within groups.
- **SMOTE-based oversampling:** Generates synthetic minority-class samples for under-represented demographic intersections.
- **Plain-English report card:** Green/Yellow/Red flags with a one-sentence explanation for every finding, designed to be readable by non-technical stakeholders.

---

## 5. Module 2 — ML Model Auditor

### 5.1 Objectives & Scope

Module 2 audits a trained ML model directly. A model can be biased even when trained on a 'clean' dataset, because algorithmic choices — loss functions, regularisation, feature selection, threshold calibration — can introduce or amplify disparities during training. This module accepts a serialised model (sklearn pickle, ONNX, or callable predict function) along with a labelled test set and produces a comprehensive fairness scorecard.

### 5.2 Real-World Motivation — The COMPAS Case

The COMPAS recidivism algorithm, analysed by ProPublica in 2016, is the defining case study for why ML model auditing matters. The system, used in US courts to inform sentencing, was found to classify Black defendants as high-risk at nearly twice the rate of white defendants with comparable criminal histories. Black defendants were 45% more likely to be falsely flagged for future general crime and 77% more likely to be falsely flagged for violent crime (Larson et al., 2016).

Critically, COMPAS does not include race as an explicit feature. The bias emerged from proxy variables — neighbourhood, employment history, prior arrest count — that are statistically correlated with race due to systemic inequities in policing. This is the canonical example of proxy discrimination, and it illustrates why fairness auditing must go beyond checking for protected attributes in the feature set.

The COMPAS case also illustrates the 'impossibility of fairness' theorem: it is mathematically impossible for a model to satisfy both calibration (equal positive predictive value across groups) and equalised odds (equal false positive/false negative rates across groups) simultaneously when base rates differ. Module 2 surfaces this trade-off explicitly and lets the user choose which fairness definition is appropriate for their context.

### 5.3 Core Detection Techniques

**Counterfactual Flip Test**

Counterfactual fairness testing — generating 'what if' instances by changing only the protected attribute and measuring whether the model output changes — is one of the most powerful and interpretable methods available. It produces concrete, human-readable evidence: 'This application was approved; an identical application differing only in the applicant's gender was rejected.'

```python
original = model.predict(sample) # John, age 32, 5yr exp → Approved
flipped = model.predict(swap(sample, gender="Female")) # Jane, identical → Rejected
if original != flipped: flag_bias(sample)
```

**Fairness Metrics Computed Post-Prediction**

| Metric | Definition | Flag Threshold |
|---|---|---|
| Demographic Parity Difference | Approval rate(unprivileged) - Approval rate(privileged) | < -0.10 |
| Equalized Odds Difference | Max of FPR diff and FNR diff across groups | > 0.10 |
| Calibration | Predicted probability accuracy equal across groups | Diff > 0.05 |
| Individual Fairness Flip Rate | % of counterfactual pairs with different decisions | > 5% |
| Predictive Parity | Positive predictive value equal across groups | Diff > 0.05 |

### 5.4 Explainability with SHAP

SHAP (SHapley Additive exPlanations), introduced by Lundberg & Lee (2017), provides game-theoretic feature importance scores for any ML model. In the context of bias detection, SHAP serves two purposes:

- **Global explanation:** Identifies which features drive decisions most strongly across the entire test set. If a feature strongly correlated with a protected attribute (e.g. ZIP code as a proxy for race) appears near the top of the global SHAP ranking, it is flagged as a potential proxy discrimination vector.
- **Subgroup comparison:** Computes separate SHAP importance rankings for each demographic subgroup. If the model relies on different features for different groups — even if overall accuracy is similar — this indicates the model is using different decision logic for different demographics.

The COMPAS XGBoost re-implementation study (Biecek, 2020) found that race and sex appeared prominently in SHAP feature importance rankings despite not being explicit model inputs, confirming that SHAP is effective at surfacing proxy bias that standard accuracy metrics miss.

### 5.5 Three-Stage Bias Pipeline

- **Pre-processing:** Reweighting and data transformation applied before model training. Kamiran & Calders (2012) show that sample reweighting can reduce disparate impact by 30-50% with less than 2% accuracy loss.
- **In-processing:** Adversarial debiasing — a secondary network simultaneously trained to predict the protected attribute from the model's internal representations, penalising the main model for encoding demographic information. Zhang et al. (2018) demonstrate this approach across hiring and credit datasets.
- **Post-processing:** Hardt et al.'s (2016) Equalised Odds Post-Processing adjusts decision thresholds per demographic group to equalise false positive and false negative rates. This requires no model retraining and can be applied to any deployed model.

### 5.6 Mitigation Strategies Offered

- Threshold adjustment per group (post-processing, no retraining required)
- Suggested sample reweighting scheme for retraining
- SHAP-guided feature removal: ranks proxy features by correlation with protected attributes and suggests removing the highest-risk ones
- Calibration recalibration using Platt scaling per subgroup

---

## 6. Module 3 — Agent Auditor

### 6.1 Objectives & Scope

Module 3 audits LLM-powered agents — any system with a system prompt that accepts natural language input and produces decisions or recommendations. The agent is treated as a black box; the module only observes inputs and outputs. This design means Module 3 works regardless of which LLM powers the agent, which framework built it, or how complex its internal pipeline is.

This module addresses a fundamentally different class of bias from Modules 1 and 2. LLM agents can exhibit: (1) explicit demographic bias when protected attributes are stated in the input; (2) implicit proxy bias when protected attributes are inferred from names, writing style, or vocabulary; (3) contextual priming bias when historical context about a person activates stereotypes; and (4) reasoning-trace bias where the model reaches the same decision but justifies it differently for different groups.

### 6.2 Five-Layer Architecture

- **Layer 1 — Context Collection:** Collects the agent's connection mode (API endpoint, pasted system prompt, or interaction log replay), the agent's decision context, and a seed input case from the user.
- **Layer 2 — Persona Grid Generation:** Constructs a factorial grid of synthetic test inputs identical in all decision-relevant attributes, varying only across protected attributes. Both explicit injection and name-based proxy testing are performed.
- **Layer 3 — Agent Interrogation Engine:** Submits all personas to the agent asynchronously, handles rate limits, parses diverse output types (binary, numeric, free-text), and stores full reasoning traces for chain-of-thought agents.
- **Layer 4 — Statistical Bias Detection:** Pure Python statistical analysis of collected outputs. No LLM is involved in this layer. Computes demographic parity, equalized odds, intersectional disparities, and reasoning-trace divergence.
- **Layer 5 — LLM Interpreter & Remediation:** A single, tightly-scoped LLM call that receives the statistical findings and produces plain-English explanations and suggested system-prompt edits.

### 6.3 Persona Grid Generation

The persona grid is the engine of the module. It generates a complete factorial crossing of all protected attribute values, ensuring every combination is tested:

```python
protected = { "gender": ["Male","Female","Non-binary"],
              "race": ["White","Black","Hispanic","Asian"],
              "age": ["24","45","62"] }

total_personas = 3 x 4 x 3 = 36 (all identical qualifications)
```

A critical subtlety is name-based proxy discrimination. LLMs infer demographics from names even when demographics are not stated explicitly. Research by Bertrand & Mullainathan (2004) established that resumes with stereotypically Black names receive 50% fewer callbacks than identical resumes with stereotypically white names. Module 3 tests both explicit attribute injection and name-based variants to detect both forms. A validated name-demographic lookup table of approximately 50 names per group is bundled with the application.

To control for LLM non-determinism, temperature is set to 0 for all calls where the user controls the model, and each persona is run 3-5 times with majority-vote aggregation. This provides a variance estimate per persona that is itself surfaced in the report.

### 6.4 Statistical Detection Engine

The detection layer is entirely deterministic — it contains no LLM calls. It computes:

- **Demographic Parity Difference:** Approval rate difference between the least-favoured and most-favoured demographic groups. US EEOC 80% rule threshold applied.
- **Welch's t-test / Mann-Whitney U:** For numeric score outputs, tests whether score distributions differ significantly across groups. p-value threshold is configurable.
- **Chi-square test:** For binary decision outputs, tests whether the distribution of decisions is independent of the protected attribute.
- **Intersectional disparity scan:** Computes metrics for every combination of protected attributes, detecting compounded bias that single-attribute analysis misses.
- **Reasoning-trace divergence:** For chain-of-thought agents, analyses whether the reasoning trace uses systematically different language or criteria for different demographic groups (keyword frequency + embedding similarity).

Findings are classified by severity:

| Level | Condition | Recommended Action |
|---|---|---|
| ■ CRITICAL | p < 0.01 AND disparity > 20% | Halt deployment. Document immediately. Legal review. |
| ■ MODERATE | p < 0.05 AND disparity > 10% | Mandatory remediation before production. |
| ■ LOW | p < 0.10 OR disparity < 10% | Monitor; revisit before next release. |
| ■ CLEAR | p >= 0.10 AND disparity < 5% | No significant bias detected. Archive report. |

### 6.5 LLM Interpreter & Remediation

The LLM's role is tightly constrained. It receives only the statistical outputs from Layer 4 and is instructed not to speculate beyond what the numbers show. This design addresses the known problem of LLM-as-judge hallucination — because the LLM has no agency in the detection step, it cannot invent bias that does not statistically exist.

The interpreter produces: (1) a plain-English explanation of each finding; (2) a targeted addition to the system prompt designed to neutralise the detected bias without altering the agent's core task; and (3) a before/after prediction of what metrics should look like after the fix is applied. After the user edits their system prompt, the full audit can be re-run to generate a quantified improvement report.

For privacy-sensitive deployments, a local-mode option uses Ollama (Mistral 7B or LLaMA 3) for the interpreter call, ensuring zero data leaves the machine. Cloud mode (Claude/GPT-4) is available for higher-quality suggestions on opt-in.

### 6.6 Research-Backed Enrichments

**CAFFE Framework Integration**

The CAFFE (Counterfactual Assessment Framework for Fairness Evaluation) framework, proposed by Cruciani et al. (2025), formalises LLM fairness test cases with explicitly defined components: prompt intent, conversational context, input variants, expected fairness thresholds, and test environment configuration. Module 3 adopts CAFFE's test case schema for structuring persona variants, enabling reproducible audit sessions that can be exported and re-run across agent versions. CAFFE's semantic similarity metrics are used as a secondary signal when evaluating reasoning-trace divergence.

**Counterfactual Flip Rate (CFR) & Mean Absolute Score Difference (MASD)**

Mayilvaghanan et al. (2025) evaluated 18 LLMs on 3,000 real-world contact-centre transcripts using two metrics well-suited to agent auditing: the Counterfactual Flip Rate (CFR — the frequency of binary judgment reversals across counterfactual pairs) and the Mean Absolute Score Difference (MASD — the average shift in confidence or evaluation scores across pairs). Their study found CFRs ranging from 5.4% to 13.0% and consistent MASD shifts, establishing baseline ranges against which Module 3 scores can be benchmarked. Contextual priming of historical performance induced the most severe degradations (CFR up to 16.4%), directly motivating the inclusion of historical-context persona variants in Module 3's grid.

**Multi-Agent Structured Reasoning**

Structured Reasoning for Fairness (Nguyen et al., 2025) proposes a multi-agent architecture in which a 'detector' agent identifies potentially biased statements and a 'reasoner' agent provides interpretable explanations. Module 3's Layer 5 adopts a lightweight version of this pattern: the statistical layer plays the role of detector, and the LLM interpreter plays the role of reasoner, but critically, the reasoner has no access to the raw agent outputs — it only sees aggregated statistics. This eliminates the false-positive risk identified in the original paper.

**Adaptive Bias-Eliciting Prompt Generation**

Romero-Arjona et al. (2025) introduce a counterfactual bias evaluation framework that iteratively refines test questions to maximise the probability of eliciting biased behaviour. Module 3 incorporates a simplified version of this idea in its 'stress test' mode: if a first-pass audit finds no significant bias, the system can generate a second round of more targeted probes based on the specific decision context, reducing false-negative risk for subtle or context-dependent biases.

---

## 7. Technical Architecture

All modules share a common Tauri desktop shell that communicates with a locally-running FastAPI server (started automatically on application launch). The Python server handles all computation. No data is sent to external services unless the user explicitly enables cloud LLM mode.

| Layer | Technology | Purpose |
|---|---|---|
| Desktop Shell | Tauri (Rust + React) | Native .exe, lightweight, ships local web UI |
| Frontend | React + Tailwind CSS | Unified dashboard across all three modules |
| Backend | Python (FastAPI, local server) | All statistical computation, ML inference, report generation |
| Dataset Module | pandas, aif360, missingno | EDA, fairness metrics, reweighting |
| Model Module | fairlearn, shap, scikit-learn | Fairness metrics, SHAP explainability, threshold adjustment |
| Agent Module | asyncio, scipy, sentence-transformers | Persona interrogation, statistics, embedding similarity |
| Local LLM | Ollama (Mistral 7B / LLaMA 3) | Privacy-preserving interpreter mode |
| Cloud LLM (opt-in) | Anthropic Claude / OpenAI GPT-4 | Higher-quality interpretation and remediation |
| Bundling | PyInstaller + Tauri bundler | Single .exe installer for Windows |
| Report Export | reportlab, matplotlib | PDF audit reports with charts |

---

## 8. References

### Module 1 — Dataset Auditor

[1] Pagano, T. P. et al. (2023). Bias and Unfairness in Machine Learning Models: A Systematic Review on Datasets, Tools, Fairness Metrics, and Identification and Mitigation Methods. Big Data and Cognitive Computing, 7(1), 15. https://doi.org/10.3390/bdcc7010015

[2] Mehrabi, N. et al. (2021). A Survey on Bias and Fairness in Machine Learning. ACM Computing Surveys, 54(6), 1–35.

[3] Pessach, D., & Shmueli, E. (2022). A Review on Fairness in Machine Learning. ACM Computing Surveys, 55(3), 1–44.

[4] Kamiran, F., & Calders, T. (2012). Data preprocessing techniques for classification without discrimination. Knowledge and Information Systems, 33(1), 1–33.

[5] González-Sendino, R. et al. (2024). A Review of Bias and Fairness in Artificial Intelligence. IJIMAI, 9(1), 5–17.

[6] Caton, S., & Haas, C. (2024). Fairness in Machine Learning: A Survey. ACM Computing Surveys, 56(7), 1–38.

[7] Uddin, S., & Lu, H. (2025). Fairness-preserving framework for machine learning: data bias quantification, model evaluation, and robustness across multiple datasets. AI and Ethics. Springer.

[8] Feldman, M. et al. (2015). Certifying and removing disparate impact. KDD 2015, 259–268.

### Module 2 — ML Model Auditor

[9] Larson, J. et al. (2016). How We Analyzed the COMPAS Recidivism Algorithm. ProPublica. https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm

[10] Angwin, J. et al. (2016). Machine Bias. ProPublica. https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing

[11] Lundberg, S., & Lee, S. I. (2017). A unified approach to interpreting model predictions. NeurIPS 2017.

[12] Hardt, M., Price, E., & Srebro, N. (2016). Equality of Opportunity in Supervised Learning. NeurIPS 2016.

[13] Zhang, B. H., Lemoine, B., & Mitchell, M. (2018). Mitigating Unwanted Biases with Adversarial Learning. AAAI/ACM AIES 2018, 335–340.

[14] Yang, J. et al. (2023). Algorithmic fairness and bias mitigation for clinical machine learning with deep reinforcement learning. Nature Machine Intelligence, 5, 884–894.

[15] Dressel, J., & Farid, H. (2018). The accuracy, fairness, and limits of predicting recidivism. Science Advances, 4(1).

[16] Biecek, P. (2020). COMPAS: Recidivism Reloaded. XAI Stories. https://pbiecek.github.io/xai_stories/story-compas.html

[17] Chouldechova, A. (2017). Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. Big Data, 5(2), 153–163.

[18] Ntoutsi, E. et al. (2020). Bias in data-driven AI systems — An introductory survey. Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery, 10(3).

### Module 3 — Agent Auditor

[19] Mayilvaghanan, K., Gupta, S., & Kumar, A. (2025). Counterfactual Fairness Evaluation of LLM-Based Contact Center Agent Quality Assurance System. arXiv:2602.14970.

[20] Cruciani, F. et al. (2025). Toward Systematic Counterfactual Fairness Evaluation of Large Language Models: The CAFFE Framework. arXiv:2512.16816.

[21] Nguyen, T. et al. (2025). Structured Reasoning for Fairness: A Multi-Agent Approach to Bias Detection in Textual Data. arXiv:2503.00355.

[22] Romero-Arjona, D. et al. (2025). Adaptive Generation of Bias-Eliciting Questions for LLMs. arXiv:2510.12857.

[23] Gallegos, I. O. et al. (2024). Bias and Fairness in Large Language Models: A Survey. Computational Linguistics, 1–79.

[24] Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg More Employable Than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination. American Economic Review, 94(4), 991–1013.

[25] Dwork, C. et al. (2012). Fairness through awareness. ITCS 2012, 214–226.

[26] Bird, S. et al. (2020). Fairlearn: A toolkit for assessing and improving fairness in AI. Microsoft Research.

[27] Bellamy, R. K. E. et al. (2019). AI Fairness 360: An Extensible Toolkit for Detecting, Understanding, and Mitigating Unwanted Algorithmic Bias. IBM Journal of Research and Development, 63(4/5).
