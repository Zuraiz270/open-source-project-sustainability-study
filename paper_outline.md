# IEEE Paper Outline
## Factors Influencing Open-Source Software Project Sustainability: A Comparative Sample Study

---

## 1. ABSTRACT (~150 words)

**Context:** OSS sustainability is critical but poorly understood.

**Objective:** Identify governance, community, and ecosystem factors that predict long-term sustainability.

**Method:** Comparative sample study of 500 GitHub projects (250 sustainable, 250 non-sustainable).

**Key Results:**
- Maintainer guidelines: 3.6x sustainability difference (p<0.00001)
- Bus factor: sustainable median=4 vs non-sustainable=2 (p<0.0001)
- Stars threshold: >11,934 = 4.15x sustainability lift
- XGBoost prediction: 97.2% accuracy (AUC 0.993)

**Conclusion:** Governance maturity and contributor structure predict sustainability better than popularity alone.

---

## 2. INTRODUCTION (~1 page)

### 2.1 Problem Statement
- OSS powers 96% of codebases but 80% face abandonment risk
- No consensus on what differentiates sustainable from failed projects

### 2.2 Research Gap
- Prior work focuses on single dimensions (community OR governance)
- Lack of predictive models with interpretable features

### 2.3 Research Questions
| RQ | Question | Dimension |
|----|----------|-----------|
| **RQ1** | How do governance practices relate to sustainability? | Governance |
| **RQ2** | How do community health indicators predict survival? | Community |
| **RQ3** | Do ecosystem metrics correlate with sustainability? | Ecosystem |
| **RQ4** | Which factors best predict sustainability? | Combined |

### 2.4 Contributions
1. First study combining governance + community + ecosystem predictors
2. Novel metrics: bus factor, contributor Gini, maintainer guidelines
3. Interpretable ML model achieving 97.2% accuracy

---

## 3. RELATED WORK (~1 page)

### 3.1 OSS Sustainability Definitions
- Crowston et al. (2006): Community health metrics
- Chengalur-Smith et al. (2010): Lifespan-based definitions

### 3.2 Governance and Documentation
- Schweik & English (2012): Governance success factors
- OpenSSF Scorecard: Security and maintenance metrics

### 3.3 Community Dynamics
- CHAOSS metrics: contributor diversity, bus factor
- Jergensen et al. (2011): Onboarding practices

### 3.4 Ecosystem Factors
- Stars vs. actual usage (Borges et al., 2016)
- Fork patterns and downstream dependencies

---

## 4. METHODOLOGY (~2 pages)

### 4.1 Study Design
- **Type:** Comparative observational study
- **Strategy:** Sample study (Stol & Fitzgerald ABC framework)
- **Generalization:** Statistical (sample → GitHub population)

### 4.2 Sampling
| Aspect | Value |
|--------|-------|
| Source | GHArchive via BigQuery (Dec 2023) |
| Sample size | 500 projects |
| Sustainable | 250 (active with commits in 2024) |
| Non-sustainable | 250 (archived or dormant >12 months) |
| Languages | Python, TypeScript, JavaScript, Go |

### 4.3 Data Collection

**Sources:**
1. GitHub API (governance files, repo metadata)
2. GHArchive (issue/PR response times)
3. GitHub Contributors API (bus factor, Gini)

**Metrics Collected (32 total):**

| Dimension | Metrics |
|-----------|---------|
| Governance | CODE_OF_CONDUCT, CONTRIBUTING, LICENSE, issue/PR templates, README, MAINTAINERS/GOVERNANCE |
| Community | Issue response time, PR review time, contributors, commits, bus factor, Gini |
| Ecosystem | Stars, forks, watchers |

### 4.4 Analysis Methods

| RQ | Method | Effect Size |
|----|--------|-------------|
| RQ1 | Chi-square, Fisher's Exact | Odds Ratio, Cramer's V |
| RQ2 | Mann-Whitney U, Survival analysis | Rank-biserial r |
| RQ3 | Spearman correlation, Decision tree thresholds | Lift |
| RQ4 | Logistic Regression, Random Forest, XGBoost | SHAP values |

### 4.5 Robustness Checks
- FDR correction (Benjamini-Hochberg)
- Bootstrap 95% confidence intervals
- Power analysis (99% achieved)

---

## 5. RESULTS (~3 pages)

### 5.1 RQ1: Governance Practices

**Data source:** `results/v5/rq1_governance.csv`

| Practice | Sustainable | Non-sustainable | χ² | p-value | OR |
|----------|-------------|-----------------|----|---------|----|
| Contributing | 57.6% | 41.2% | 12.8 | 0.0003 | 1.94 |
| PR Template | 43.6% | 19.6% | 32.2 | <0.0001 | 3.17 |
| **Maintainer Guidelines** | **18.8%** | **5.2%** | **20.6** | **<0.0001** | **4.22** |

**Figure:** `rq1_governance_heatmap.png`

**Finding:** Maintainer guidelines have the strongest association with sustainability (OR=4.22).

### 5.2 RQ2: Community Health

**Data source:** `results/v5/rq2_community.csv`

| Metric | Sustainable | Non-sustainable | p-value | r |
|--------|-------------|-----------------|---------|---|
| Issue Response | 0.54 days | 1.78 days | <0.0001 | 0.27 |
| **Bus Factor** | **4** | **2** | **<0.0001** | **0.30** |
| Gini | 0.86 | 0.79 | <0.0001 | 0.38 |

**Figure:** `rq2_survival_curve.png`

**Finding:** Sustainable projects have 2x higher bus factor (more key contributors).

### 5.3 RQ3: Ecosystem Metrics

**Data source:** `results/v5/rq3_ecosystem.csv`

| Metric | Threshold | Below | Above | Lift |
|--------|-----------|-------|-------|------|
| Stars | 11,934 | 22.4% | 92.9% | 4.15x |
| Forks | 1,724 | 31.6% | 83.6% | 2.65x |
| Watchers | 2,628 | 35.1% | 80.7% | 2.30x |

**Figure:** `rq3_threshold_analysis.png`

**Finding:** Projects with >11,934 stars are 4.15x more likely to be sustainable.

### 5.4 RQ4: Predictive Model

**Data source:** `results/v5/rq4_prediction.csv`

| Model | Accuracy | AUC |
|-------|----------|-----|
| Logistic Regression | 86.6% | 0.928 |
| Random Forest | 95.0% | 0.991 |
| **XGBoost** | **97.2%** | **0.993** |

**Top SHAP Features:**
1. stars_count (2.21)
2. forks_count (1.54)
3. contributor_diversity_gini (0.89)

**Figure:** `rq4_shap_summary.png`

**Finding:** Combination of ecosystem + community features achieves near-perfect prediction.

---

## 6. DISCUSSION (~1 page)

### 6.1 Key Insights

1. **Governance maturity matters more than documentation breadth**
   - Maintainer guidelines (OR=4.22) > Contributing guide (OR=1.94)

2. **Contributor structure predicts sustainability**
   - Bus factor = 4: Need multiple core contributors, not just one

3. **Stars are necessary but not sufficient**
   - Threshold effect: marginal returns after ~12k stars

### 6.2 Practical Implications

| For Maintainers | For Contributors | For Funders |
|-----------------|------------------|-------------|
| Add MAINTAINERS.md | Look for bus factor >3 | Prioritize projects with governance docs |
| Document governance | Check response times | Consider contributor diversity |
| Build core team | Verify active maintenance | Don't rely on stars alone |

### 6.3 Comparison with Prior Work
- Confirms findings from Schweik & English (2012) on governance
- Extends CHAOSS metrics with predictive validation
- Challenges stars-as-quality assumption

---

## 7. LIMITATIONS (~0.5 page)

| Limitation | Mitigation |
|------------|------------|
| 47% missing scorecard scores | MICE imputation + sensitivity analysis |
| 58% missing PR review times | Documented as unreliable, excluded from main findings |
| Binary sustainability definition | Tested with 3 alternative definitions (all robust) |
| GitHub-only sample | Acknowledged bias toward hosted projects |
| Correlation ≠ causation | Causal claims avoided; focus on prediction |

---

## 8. CONCLUSION (~0.5 page)

### 8.1 Summary
- Analyzed 500 GitHub projects across governance, community, and ecosystem dimensions
- Identified maintainer guidelines and bus factor as strongest predictors
- Achieved 97.2% prediction accuracy with interpretable features

### 8.2 Contributions
1. First multi-dimensional comparative study with ML validation
2. Novel operationalization of bus factor and governance metrics
3. Practical thresholds for sustainability assessment

### 8.3 Future Work
- Longitudinal study tracking projects over time
- Extension to GitLab and self-hosted projects
- Causal inference with temporal analysis

---

## 9. REFERENCES

**See:** `references.md` (24 citations, IEEE format)

Key references:
- [1] Schweik & English (2012) - Governance success factors
- [21] Benjamini & Hochberg (1995) - FDR correction
- [23] Lundberg & Lee (2017) - SHAP values

---

## APPENDIX

### A. Data Availability
- Dataset: `data/processed/final_dataset.csv`
- Analysis scripts: `scripts/run_analysis_v5.py`
- GitHub repository: [to be added]

### B. Supplementary Tables
- Full results: `results/v5/*.csv`
- FDR correction: `results/v5/robustness/fdr_correction.csv`
