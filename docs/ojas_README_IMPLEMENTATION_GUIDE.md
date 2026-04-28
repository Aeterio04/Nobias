# Agent Audit System - Documentation Index

> **Complete guide to understanding and using the FairSight Agent Audit System**

---

## 📚 Documentation Structure

This implementation guide consists of three complementary documents:

### 1. **AGENT_AUDIT_IMPLEMENTATION_GUIDE.md** (Main Guide)
**For**: Comprehensive understanding and implementation

**Contents**:
- Executive summary and research foundations
- Complete system architecture (5 layers)
- All connection modes and audit tiers
- Detailed implementation examples
- Input/output examples for each tier
- Best practices and troubleshooting
- Advanced topics and integrations
- Research papers and compliance standards

**Length**: ~500 lines  
**Read time**: 30-45 minutes  
**Use when**: You need complete understanding or reference

---

### 2. **AGENT_AUDIT_QUICK_START.md** (Quick Start)
**For**: Getting started in 5 minutes

**Contents**:
- Installation instructions
- 5-minute working example
- Understanding results (severity, EEOC)
- Common use cases
- Fixing bias (3-step process)
- Quick troubleshooting

**Length**: ~200 lines  
**Read time**: 5-10 minutes  
**Use when**: You want to start immediately

---

### 3. **AGENT_AUDIT_VISUAL_SUMMARY.md** (Visual Guide)
**For**: Visual learners and quick reference

**Contents**:
- System overview diagrams
- Connection modes visualization
- Audit tiers comparison
- Persona generation flow
- Two-pass optimization diagram
- Metrics explained visually
- Severity classification chart
- Workflow diagram
- Cost breakdown

**Length**: ~300 lines  
**Read time**: 10-15 minutes  
**Use when**: You prefer visual explanations

---

## 🚀 Quick Navigation

### I want to...

**...understand what this system does**
→ Read: Executive Summary in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: System Overview in AGENT_AUDIT_VISUAL_SUMMARY.md

**...run my first audit in 5 minutes**
→ Read: AGENT_AUDIT_QUICK_START.md

**...understand the architecture**
→ Read: System Architecture in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: 5-Layer Pipeline in AGENT_AUDIT_VISUAL_SUMMARY.md

**...see example code**
→ Read: Example Workflows in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: 5-Minute Example in AGENT_AUDIT_QUICK_START.md

**...understand the metrics**
→ Read: Key Concepts in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: Metrics Explained in AGENT_AUDIT_VISUAL_SUMMARY.md

**...choose the right tier**
→ Read: Access Modes & Tiers in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: Audit Tiers in AGENT_AUDIT_VISUAL_SUMMARY.md

**...fix bias in my agent**
→ Read: Remediation Strategy in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: Fixing Bias in AGENT_AUDIT_QUICK_START.md

**...troubleshoot issues**
→ Read: Troubleshooting in AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
→ Or: Troubleshooting in AGENT_AUDIT_QUICK_START.md

---

## 📖 Recommended Reading Order

### For Developers (First Time)
1. **AGENT_AUDIT_QUICK_START.md** - Get started immediately
2. **AGENT_AUDIT_VISUAL_SUMMARY.md** - Understand the system visually
3. **AGENT_AUDIT_IMPLEMENTATION_GUIDE.md** - Deep dive when needed

### For Researchers
1. **AGENT_AUDIT_IMPLEMENTATION_GUIDE.md** - Complete technical details
2. Research Papers section - Understand foundations
3. Advanced Topics section - Custom implementations

### For Compliance Officers
1. **AGENT_AUDIT_IMPLEMENTATION_GUIDE.md** - Focus on:
   - Key Concepts (metrics)
   - Severity Classification
   - Compliance Standards
2. **AGENT_AUDIT_VISUAL_SUMMARY.md** - Metrics Explained section

### For Product Managers
1. **AGENT_AUDIT_VISUAL_SUMMARY.md** - System overview
2. **AGENT_AUDIT_QUICK_START.md** - Use cases
3. Cost Breakdown in AGENT_AUDIT_VISUAL_SUMMARY.md

---

## 🎯 Key Takeaways

### What This System Does
Detects bias in AI agents using counterfactual testing and research-validated metrics. Treats agents as black boxes and measures discrimination that would be legally defensible in court.

### Why It's Special
- **Research-Backed**: Integrates 4 peer-reviewed papers
- **Cost-Optimized**: 82% token reduction
- **Legally Defensible**: EEOC-compliant, tamper-evident
- **Privacy-First**: Core detection runs locally

### How to Use It
```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="Your agent prompt...",
    seed_case="Your test case...",
    api_key="gsk_...",
    mode="standard",
)
```

### What You Get
- CFR (Counterfactual Flip Rate): How often decisions flip
- EEOC AIR: Legal compliance status
- Severity: CRITICAL/MODERATE/LOW/CLEAR
- Remediation: Concrete prompt suggestions

---

## 📊 System Capabilities

### Connection Modes
1. **System Prompt**: Test during development
2. **API Endpoint**: Test production agents
3. **Log Replay**: Privacy-friendly historical audits

### Audit Tiers
1. **Quick** (50k tokens): ~2 min, ~$0.05
2. **Standard** (80k tokens): ~5 min, ~$0.17
3. **Full** (130k tokens): ~30 min, ~$0.27

### Key Metrics
- **CFR**: Decision flip rate
- **MASD**: Score shift magnitude
- **EEOC AIR**: Legal compliance (80% rule)
- **SSS**: Decision consistency

### Severity Levels
- **CRITICAL** (CFR > 15%): Do not deploy
- **MODERATE** (CFR 10-15%): Remediate before production
- **LOW** (CFR 5-10%): Monitor
- **CLEAR** (CFR < 5%): No action needed

---

## 🔧 Additional Resources

### Code Examples
- `examples/full_audit_example.py` - All 3 API levels
- `examples/optimized_audit_example.py` - Token optimization
- `examples/langgraph_agent_server.py` - API endpoint testing

### Library Documentation
- `library/agent_audit/QUICKSTART.md` - Library quickstart
- `library/agent_audit/API_REFERENCE.md` - Complete API reference
- `library/agent_audit/LIBRARY_DESIGN.md` - Architecture details

### Development Logs
- `docs/ojas_logs.md` - Implementation history
- `docs/ojas_TOKEN_OPTIMIZATION.md` - Optimization details
- `docs/FAIRSIGHT_PHASE2_COMPLETE.md` - Compliance features

### Research Papers
1. CAFFE (Parziale et al., 2025) - Test schema
2. CFR/MASD (Mayilvaghanan et al., 2025) - Primary metrics
3. Structured Reasoning (Huang & Fan, 2025) - Interpretation
4. Adaptive Probing (Staab et al., 2025) - Stress testing

---

## 🆘 Getting Help

### Common Issues
- **"All decisions ambiguous"** → Add response_normalizer
- **"Rate limit exceeded"** → Reduce rate_limit_rps
- **"Audit takes too long"** → Use quick mode
- **"EEOC AIR is 0.0%"** → Use borderline seed case

### Support Channels
- **Documentation**: This guide + library docs
- **Examples**: `examples/` directory
- **GitHub Issues**: Report bugs
- **Development Logs**: `docs/ojas_logs.md`

---

## ✅ Quick Checklist

Before running your first audit:
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Got API key (https://console.groq.com/)
- [ ] Set environment variable (`export GROQ_API_KEY="gsk_..."`)
- [ ] Prepared system prompt
- [ ] Created borderline seed case
- [ ] Chose audit mode (quick/standard/full)

After running audit:
- [ ] Reviewed overall severity
- [ ] Checked EEOC AIR status
- [ ] Read interpretation
- [ ] Applied prompt suggestions (if needed)
- [ ] Re-audited (if remediated)
- [ ] Exported reports for documentation

---

## 📈 Success Metrics

### Development
- Run quick scan after each major prompt change
- Target: CLEAR or LOW severity
- Budget: ~$0.05 per audit

### Production
- Run standard audit before each deployment
- Target: CLEAR severity, EEOC COMPLIANT
- Budget: ~$0.17 per audit

### Compliance
- Run full investigation annually
- Target: Documented audit trail
- Budget: ~$0.27 per audit

---

## 🎓 Learning Path

### Beginner (Day 1)
1. Read AGENT_AUDIT_QUICK_START.md
2. Run 5-minute example
3. Understand severity levels

### Intermediate (Week 1)
1. Read AGENT_AUDIT_VISUAL_SUMMARY.md
2. Try all 3 connection modes
3. Experiment with different tiers

### Advanced (Month 1)
1. Read AGENT_AUDIT_IMPLEMENTATION_GUIDE.md
2. Implement before/after comparison
3. Integrate with CI/CD

### Expert (Month 3)
1. Study research papers
2. Implement custom metrics
3. Contribute to development

---

## 📝 Version Information

**Last Updated**: 2026-04-26  
**Version**: 1.0.0  
**Status**: Production Ready ✅

**What's New**:
- Complete 5-layer pipeline
- 82% token optimization
- FairSight compliance (EEOC, EU AI Act)
- Three API levels
- Comprehensive documentation

**Coming Soon**:
- PDF report generation
- Web dashboard
- Batch processing
- Additional LLM backends

---

## 🙏 Acknowledgments

This system integrates research from:
- CAFFE framework (Parziale et al., 2025)
- CFR/MASD metrics (Mayilvaghanan et al., 2025)
- Structured reasoning (Huang & Fan, 2025)
- Adaptive probing (Staab et al., 2025)
- Name-demographic mapping (Bertrand & Mullainathan, 2004)

Built with support from the FairSight project team.

---

**Ready to start?** → Open AGENT_AUDIT_QUICK_START.md

**Need details?** → Open AGENT_AUDIT_IMPLEMENTATION_GUIDE.md

**Prefer visuals?** → Open AGENT_AUDIT_VISUAL_SUMMARY.md
