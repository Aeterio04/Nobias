// ── Documentation — Redesigned ──
export function documentationPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="settings-content">
      <div class="anim-1"><h1 class="page-title">Documentation</h1><p class="page-subtitle">Learn how to use Nobias to audit your AI systems for bias and compliance.</p></div>
      <div class="anim-2">
        <div class="card mb-4"><div class="card-title">Getting Started</div><p style="font-size:14px;color:var(--c-text-3);line-height:1.6">Nobias provides three main auditing modules — Dataset, Model, and Agent — each designed to detect different types of bias in your AI pipeline. Start by uploading your data or configuring your agent, then run an audit to get actionable findings.</p></div>
        <div class="card mb-4"><div class="card-title">Dataset Auditor</div><p style="font-size:14px;color:var(--c-text-3);line-height:1.6;margin-bottom:12px">Upload a CSV, XLSX, or Parquet dataset and select protected attributes. The auditor checks for representation imbalance, label bias, feature-attribute correlations, and intersectional patterns.</p><div style="display:flex;gap:8px"><span class="badge badge-accent">7 ANALYSIS PHASES</span><span class="badge badge-accent">AUTO-REMEDIATION</span></div></div>
        <div class="card mb-4"><div class="card-title">Model Auditor</div><p style="font-size:14px;color:var(--c-text-3);line-height:1.6;margin-bottom:12px">Upload a trained model plus a test dataset. The auditor evaluates demographic parity, equalized odds, counterfactual flip rates, calibration, and predictive parity.</p><div style="display:flex;gap:8px"><span class="badge badge-violet">5 FAIRNESS METRICS</span><span class="badge badge-violet">COUNTERFACTUAL</span></div></div>
        <div class="card mb-4"><div class="card-title">Agent Auditor</div><p style="font-size:14px;color:var(--c-text-3);line-height:1.6;margin-bottom:12px">Configure your LLM agent's system prompt and API. The auditor generates synthetic personas and tests for explicit attribute bias, name-based proxy discrimination, and context priming effects.</p><div style="display:flex;gap:8px"><span class="badge badge-teal">SYNTHETIC PERSONAS</span><span class="badge badge-teal">PROMPT SURGERY</span></div></div>
        <div class="card"><div class="card-title">Severity Levels</div><div style="display:flex;flex-direction:column;gap:12px;margin-top:8px">
          <div style="display:flex;align-items:center;gap:12px"><span class="badge badge-critical">CRITICAL</span><span style="font-size:13px;color:var(--c-text-3)">Bias exceeds legal/ethical thresholds. Immediate action required.</span></div>
          <div style="display:flex;align-items:center;gap:12px"><span class="badge badge-moderate">MODERATE</span><span style="font-size:13px;color:var(--c-text-3)">Notable bias detected. Review and remediation recommended.</span></div>
          <div style="display:flex;align-items:center;gap:12px"><span class="badge badge-low">LOW</span><span style="font-size:13px;color:var(--c-text-3)">Minor patterns observed. Monitor in future audits.</span></div>
          <div style="display:flex;align-items:center;gap:12px"><span class="badge badge-clear">CLEAR</span><span style="font-size:13px;color:var(--c-text-3)">No significant bias detected. System performing fairly.</span></div>
        </div></div>
      </div>
    </div>
  `;
  return d;
}
