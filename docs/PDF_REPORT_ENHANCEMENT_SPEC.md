# PDF Report Enhancement Specification

## Current State
The PDF report includes basic sections:
1. Health & Metadata (audit ID, duration, API calls)
2. Results Overview (severity, CFR, findings count)
3. Severity breakdown chart
4. Detailed findings table
5. Remediation suggestions

## Missing Critical Information (from JSON)

### 1. EEOC Compliance Section
- **AIR (Adverse Impact Ratio)** for each attribute
- Legal status (COMPLIANT/WARNING/VIOLATION)
- Risk level assessment
- Approval rates by demographic group
- Visual: Bar chart showing approval rates by group

### 2. Statistical Validity Section
- **Stochastic Stability Score (SSS)** and classification
- Trustworthiness rating
- **Bias-Adjusted CFR** vs Raw CFR comparison
- **Confidence Intervals** for all findings
- **Bonferroni Correction** results
- Visual: CI error bars for key metrics

### 3. Test Configuration Details
- Protected attributes tested
- Persona generation strategy (pairwise/factorial)
- Test types breakdown (baseline, pairwise, name_proxy, context_primed)
- Number of runs per persona
- Visual: Pie chart of test type distribution

### 4. Decision Distribution Analysis
- Positive/Negative/Ambiguous breakdown
- Approval rate trends
- Visual: Pie chart of decision distribution

### 5. Variance & Stability Analysis
- Mean decision variance across personas
- High variance persona count
- Stability classification
- Visual: Histogram of decision variances

### 6. Per-Attribute Deep Dive
For each protected attribute:
- CFR value and p-value
- EEOC AIR and legal status
- Approval rates by group
- Pairwise comparisons
- Visual: Grouped bar chart per attribute

### 7. Model Fingerprint
- Exact model ID and version
- Temperature and max_tokens
- Backend used
- System prompt hash
- Timestamp for reproducibility

### 8. Audit Integrity
- SHA-256 hashes (audit, prompts, responses, config)
- Tamper-evident verification
- Timestamp

### 9. Benchmark Comparison
- Current CFR vs industry benchmarks (5.4%-13%)
- Visual: Gauge chart showing position relative to benchmarks
- Interpretation of where the agent stands

### 10. Raw Response Analysis
- Sample raw outputs from personas
- Response length statistics
- Common patterns in reasoning

## Recommended PDF Structure

### Executive Summary (Page 1)
- Overall verdict (COMPLIANT/WARNING/VIOLATION)
- Key metrics dashboard
- Risk assessment
- Quick recommendations

### Section 1: Audit Metadata (Page 2)
- All health metrics
- Model fingerprint
- Test configuration
- Audit integrity hashes

### Section 2: Statistical Results (Pages 3-4)
- Overall CFR and severity
- Per-attribute findings with charts
- EEOC AIR results with legal status
- Benchmark comparison

### Section 3: Validity & Confidence (Page 5)
- Stochastic stability analysis
- Confidence intervals
- Bonferroni correction
- Bias-adjusted CFR

### Section 4: Decision Analysis (Page 6)
- Decision distribution
- Variance analysis
- Persona-level insights
- Test type breakdown

### Section 5: Remediation (Page 7)
- Interpretation and assessment
- Prioritized recommendations
- Specific prompt suggestions

### Section 6: Appendix (Pages 8+)
- Detailed findings table
- Sample raw outputs
- Technical notes
- Glossary of metrics

## Visual Enhancements Needed

1. **Gauge Chart**: Overall CFR vs benchmarks
2. **Bar Charts**: Approval rates by demographic group (per attribute)
3. **Pie Charts**: Decision distribution, test type distribution
4. **Histogram**: Decision variance distribution
5. **Error Bars**: Confidence intervals for CFR findings
6. **Heatmap**: Pairwise comparison matrix (if multiple attributes)
7. **Timeline**: Audit execution timeline
8. **Risk Matrix**: Severity vs confidence 2D plot

## Color Coding

- **COMPLIANT**: Green (#27ae60)
- **WARNING**: Orange (#f39c12)
- **VIOLATION**: Red (#e74c3c)
- **CLEAR**: Light green (#2ecc71)
- **LOW**: Yellow (#f1c40f)
- **MODERATE**: Orange (#e67e22)
- **CRITICAL**: Dark red (#c0392b)

## Implementation Priority

1. **High Priority** (Must Have):
   - EEOC compliance section with AIR
   - Stability score and classification
   - Per-attribute approval rate charts
   - Executive summary page

2. **Medium Priority** (Should Have):
   - Confidence intervals visualization
   - Benchmark comparison gauge
   - Decision distribution analysis
   - Model fingerprint details

3. **Low Priority** (Nice to Have):
   - Raw response samples
   - Heatmap visualizations
   - Timeline charts
   - Glossary appendix
