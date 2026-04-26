// ── Model Results — Redesigned ──
export function modelResultsPage(nav) {
  const d = document.createElement('div');
  d.innerHTML = `
    <div class="anim-1"><div class="tabs"><button class="tab active">Overview</button><button class="tab">Metrics</button><button class="tab">Explainability</button><button class="tab">Findings</button></div></div>
    <div class="verdict verdict-critical anim-1">
      <div style="flex:1">
        <div class="verdict-title">CRITICAL BIAS DETECTED</div>
        <div class="verdict-stats">5 findings · <span style="color:var(--c-critical)">2 critical</span> · <span style="color:var(--c-moderate)">2 moderate</span> · <span style="color:var(--c-low)">1 low</span></div>
        <div class="verdict-meta" style="margin-top:8px">Model: <code class="mono" style="font-size:12px">hiring_classifier.pkl</code> (RandomForestClassifier) · Tested on 3,421 samples</div>
      </div>
      <div class="verdict-actions"><button class="btn btn-secondary btn-sm">Export PDF</button><button class="btn btn-secondary btn-sm">Export JSON</button></div>
    </div>
    <div class="section anim-2">
      <div class="section-title mb-6">Fairness Scorecard</div>
      <div class="grid-5">
        <div class="scorecard failed"><div class="scorecard-top"><div class="scorecard-title">Demographic Parity</div><span style="font-size:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid var(--c-critical-bdr);background:var(--c-critical-bg);color:var(--c-critical)">FAILED</span></div><div class="scorecard-value" style="color:var(--c-critical)">0.63</div><div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:63%;background:var(--c-critical)"></div></div><div class="scorecard-threshold">Threshold: <span class="mono">0.80</span></div></div>
        <div class="scorecard failed"><div class="scorecard-top"><div class="scorecard-title">Equalized Odds</div><span style="font-size:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid var(--c-critical-bdr);background:var(--c-critical-bg);color:var(--c-critical)">FAILED</span></div><div class="scorecard-value" style="color:var(--c-critical)">0.71</div><div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:71%;background:var(--c-critical)"></div></div><div class="scorecard-threshold">Threshold: <span class="mono">0.80</span></div></div>
        <div class="scorecard warning"><div class="scorecard-top"><div class="scorecard-title">Counterfactual Flip Rate</div><span style="font-size:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid var(--c-moderate-bdr);background:var(--c-moderate-bg);color:var(--c-moderate)">MODERATE</span></div><div class="scorecard-value" style="color:var(--c-moderate)">11.2%</div><div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:22%;background:var(--c-moderate)"></div></div><div class="scorecard-threshold">Target: <span class="mono">&lt; 5%</span></div></div>
        <div class="scorecard passed"><div class="scorecard-top"><div class="scorecard-title">Calibration</div><span style="font-size:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid var(--c-clear-bdr);background:var(--c-clear-bg);color:var(--c-clear)">PASSED</span></div><div class="scorecard-value" style="color:var(--c-clear)">0.94</div><div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:94%;background:var(--c-clear)"></div></div><div class="scorecard-threshold">Threshold: <span class="mono">0.80</span></div></div>
        <div class="scorecard passed"><div class="scorecard-top"><div class="scorecard-title">Predictive Parity</div><span style="font-size:10px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid var(--c-clear-bdr);background:var(--c-clear-bg);color:var(--c-clear)">PASSED</span></div><div class="scorecard-value" style="color:var(--c-clear)">0.88</div><div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:88%;background:var(--c-clear)"></div></div><div class="scorecard-threshold">Threshold: <span class="mono">0.80</span></div></div>
      </div>
    </div>
  `;
  return d;
}
