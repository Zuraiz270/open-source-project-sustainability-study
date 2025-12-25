# ESE Assignment 2: Research Proposal

## Final Topic Selection

# "Factors Influencing Open Source Project Sustainability: A Multi-Dimensional Study"

---

## 📋 Document Information

| Aspect             | Details                                           |
| ------------------ | ------------------------------------------------- |
| **Course**   | Evidence-based Software Engineering (ESE-ESEng-M) |
| **Weight**   | 60% of final grade (6 ECTS course)                |
| **Deadline** | February 2, 2026                                  |
| **Format**   | IEEE Conference Proceedings (10 pages + 2 refs)   |

---

# 1. Introduction (Problem & Motivation)

## 1.1 The Problem

Open source software (OSS) forms the backbone of modern software infrastructure, from operating systems to web frameworks to machine learning libraries. Yet despite this critical importance, **a large proportion of OSS projects fail to achieve long-term sustainability**. Research suggests that many GitHub projects become inactive within a few years of creation [Coelho & Valente, 2017].

The software engineering community and industry practitioners commonly evaluate projects using **easily accessible but superficial metrics**: GitHub stars, fork counts, and download statistics. However, these popularity indicators fail to capture the true health and sustainability of a project. A project with 50,000 stars may be abandoned by its maintainers, while a less visible project with 500 stars may thrive with an active, healthy community for decades.

This disconnect creates significant problems for practitioners:

- **Software teams** cannot reliably assess which dependencies will remain maintained
- **Contributors** struggle to identify projects worth investing their time in
- **Organizations** lack evidence-based criteria for evaluating OSS adoption decisions
- **Maintainers** don't know which practices actually predict long-term success

## 1.2 The Gap

Previous research has examined individual factors affecting OSS success (governance models, community dynamics, or technical quality) in isolation. However, **few large-scale studies have simultaneously investigated how governance practices, community health indicators, and popularity metrics relate to project sustainability**.

Furthermore, existing popularity metrics (stars, forks) have rarely been validated against long-term project survival and maintenance outcomes.

## 1.3 Our Contribution

This study provides an **evidence-based, multi-dimensional investigation** of factors that distinguish sustainable OSS projects from those that fail. By analyzing governance, community, ecosystem, and popularity metrics together, we aim to:

1. **Identify** which governance, community, and ecosystem factors differentiate sustainable from abandoned projects
2. **Validate** whether traditional popularity metrics actually predict long-term sustainability

## 1.4 Practical Significance

Our findings will benefit:

- **Project maintainers**: Evidence-based practices for building sustainable projects
- **Contributors**: Criteria for identifying healthy projects to join
- **Organizations**: Risk assessment framework for OSS dependency decisions
- **Researchers**: Validated sustainability metrics for future studies

---

# 2. Research Questions

| # | Research Question | Dimension | Justification |
|---|-------------------|-----------|---------------|
| **RQ1** | What governance and documentation practices (presence of CONTRIBUTING.md, CODE_OF_CONDUCT, explicit maintainer guidelines, responsive issue templates) differentiate projects that maintain long-term consistent activity from those that become inactive? | Governance | Tests assumption that governance maturity predicts sustainability; actionable for maintainers |
| **RQ2** | How do community health indicators (median issue response time, PR review turnaround, contributor diversity index, maintainer bus factor) correlate with project survival probability over time? | Community | Quantifies community dynamics impact; uses established CHAOSS metrics for validity |
| **RQ3** | Does a project's ecosystem position (number of dependent packages, position in dependency network) correlate with its long-term sustainability? | Ecosystem | Explores whether being critical infrastructure helps survival |
| **RQ4** | To what extent do traditional popularity metrics (stars, forks, downloads) predict actual project sustainability compared to governance, community, and ecosystem factors? | Validation | Directly challenges industry assumptions; high practitioner relevance |
---

# 3. Research Method

## 3.1 Study Type: Comparative Sample Study

We conduct a **comparative observational study** using repository mining, comparing projects that achieved long-term sustainability against those that did not.

### Methodological Justification

| Choice                           | Justification                                                                          | Alternative Considered                             |
| -------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Sample study**           | Enables statistical generalization; appropriate for distribution/correlation questions | Case study (rejected: lacks generalizability)      |
| **Comparative design**     | Directly answers "what differentiates" questions; controls for confounds               | Pure correlational (rejected: harder to interpret) |
| **Quantitative focus**     | RQs require measurable indicators; statistical tests provide objectivity               | Mixed methods (rejected: time constraints, scope)  |
| **Retrospective analysis** | Projects need time to demonstrate survival/failure; prospective infeasible             | Prospective (rejected: impossible in timeframe)    |

### Alignment with Course Framework

Per Stol & Fitzgerald's ABC framework (Lecture 5):

- **Setting**: Neutral (analyzing existing data without manipulation)
- **Strategy**: Sample study ("referendum" - studying distribution in population)
- **Generalization**: Statistical (sample → GitHub population)

## 3.2 Sampling Strategy

### Population Definition

| Aspect                      | Definition                                                                          | Rationale                                                            |
| --------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Target population** | All non-fork, public GitHub repositories with ≥100 stars created between 2015-2020 | Provides a visibility threshold; sufficient time to observe outcomes |
| **Sampling frame**    | GHArchive via BigQuery filtered by criteria                                     | Comprehensive, updated hourly, 2011-present                              |

### Sample Selection: Stratified Purposive Sampling

```
Sample Structure (n = 500 projects total)
├── Sustainable Projects (n = 250)
│   ├── Definition: Active commits in last 6 months + issues being closed
│   ├── Selection: Random sample from qualifying projects
│   └── Stratification: By language (Python, JavaScript, Java, Go, C++ - 50 each)
│
└── Non-Sustainable Projects (n = 250)
    ├── Definition: No commits in >18 months OR explicit "archived/unmaintained"
    ├── Selection: Random sample from qualifying projects
    ├── Stratification: Matched by initial metrics (stars at 1 year, contributors)
    └── Purpose: Controls for initial popularity confound
```

### Sample Size Justification

- **Statistical power**: n=500 provides >90% power to detect medium effect sizes (d=0.5) at α=0.05
- **Regression requirements**: Rule of thumb: 10-20 observations per predictor; we have ~15 predictors → need 150-300 minimum
- **Stratification**: 50 per language (5 languages) ensures language-specific patterns detectable

### Critique & Mitigation

| Potential Criticism                                       | Our Response                                                |
| --------------------------------------------------------- | ----------------------------------------------------------- |
| "100 stars is arbitrary"                                  | Sensitivity analysis with 50 and 200 star thresholds        |
| "Language stratification biases toward popular languages" | Explicitly acknowledged; findings scoped to major languages |
| "Matching on initial metrics is imperfect"                | Include initial metrics as control variables in regression  |

## 3.3 Operationalization of Variables

### Outcome Variable: Project Sustainability

| Status                    | Operational Definition                                                                  | Measurement                 |
| ------------------------- | --------------------------------------------------------------------------------------- | --------------------------- |
| **Sustainable**     | (a) ≥1 commit in last 6 months AND (b) ≥50% of issues from last year closed/addressed | GHArchive + GitHub API      |
| **Non-Sustainable** | (a) No commits in >18 months OR (b) Explicitly archived/marked unmaintained             | GHArchive + README analysis |

### Independent Variables (RQ1: Governance)

| Variable                 | Measurement                             | Source        |
| ------------------------ | --------------------------------------- | ------------- |
| CONTRIBUTING.md presence | Binary (yes/no)                         | GitHub API    |
| CONTRIBUTING.md quality  | Word count + checklist presence (proxy) | Text analysis |
| CODE_OF_CONDUCT presence | Binary                                  | GitHub API    |
| LICENSE type             | Categorical (permissive/copyleft/none)  | GitHub API    |
| Issue template presence  | Binary                                  | GitHub API    |
| PR template presence     | Binary                                  | GitHub API    |

### Independent Variables (RQ2: Community Health)

| Variable                  | Measurement                                           | Source     |
| ------------------------- | ----------------------------------------------------- | ---------- |
| Issue response time       | Median days to first response                         | GHArchive  |
| PR review time            | Median days to first review                           | GHArchive  |
| Contributor diversity     | Gini coefficient of commit distribution               | GHArchive  |
| Bus factor                | Number of contributors responsible for 50% of commits | GHArchive  |
| Maintainer count          | Contributors with merge permissions                   | GitHub API |
| New contributor retention | % of first-time contributors who contribute again     | GHArchive  |

### Independent Variables (RQ3: Ecosystem Position)

| Variable | Measurement | Source |
|----------|-------------|--------|
| Dependent package count | Number of packages that depend on this project | deps.dev / Libraries.io |
| Reverse dependency depth | How many layers of dependencies include this | deps.dev / Libraries.io |
| Ecosystem centrality | PageRank or similar in dependency graph | deps.dev / Libraries.io |

### Independent Variables (RQ4: Popularity Metrics)

| Variable | Measurement | Source |
|----------|-------------|--------|
| Star count | At 1-year mark (to avoid survivorship bias) | GHArchive |
| Fork count | At 1-year mark | GHArchive |
| Watcher count | At 1-year mark | GHArchive |

### Control Variables

| Variable                  | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| Project age               | Older projects had more time to establish |
| Primary language          | Language ecosystems differ                |
| Initial contributor count | Larger teams may have advantages          |
| Domain (if detectable)    | Some domains more active than others      |

---

# 4. Data Sources

## 4.1 Primary Data Sources

| Source | Purpose | Access | Freshness |
|--------|---------|--------|-----------|
| **GHArchive** (BigQuery) | Activity history (commits, issues, PRs, stars) | `githubarchive` dataset on BigQuery | Updated hourly, 2011-present |
| **OpenSSF Scorecard** | Governance metrics (CONTRIBUTING.md, CODE_OF_CONDUCT, etc.) | BigQuery: `openssf:scorecardcron.scorecard-v2_latest` | Updated weekly |
| **deps.dev** (Open Source Insights) | Dependency network, ecosystem position (RQ3) | BigQuery: `deps_dev_v1` | Hourly for active packages |
| **GitHub REST API** | File presence fallback, current metadata | https://docs.github.com/en/rest | Real-time |

## 4.2 Supplementary Data Sources

| Source | Purpose | Access |
|--------|---------|--------|
| **Libraries.io** | C++ dependency data (deps.dev doesn't support C/C++) | Zenodo dump or API |
| **CHAOSS Metrics Models** | Standardized metric definitions | https://chaoss.community/ |

## 4.3 Data Extraction Strategy

```
Data Collection Pipeline
│
├── Phase 1: Sample Selection (Week 8)
│   ├── Query GHArchive via BigQuery
│   ├── Filter: stars ≥100, created 2015-2020, non-fork, language in [Python, JS, Java, Go, C++]
│   ├── Classify as sustainable/non-sustainable using activity cutoffs
│   ├── Stratified random sampling (50 per language per group)
│   └── Output: project_sample.csv (500 projects)
│
├── Phase 2: Governance Data (Week 9)
│   ├── Query OpenSSF Scorecard for CODE_OF_CONDUCT, CONTRIBUTING scores
│   ├── GitHub API fallback for repos not in Scorecard
│   └── Output: governance_metrics.csv
│
├── Phase 3: Community Data (Week 9-10)
│   ├── GHArchive: Extract issue/PR event timelines
│   ├── Calculate response times, review times
│   ├── Calculate contributor diversity metrics
│   └── Output: community_metrics.csv
│
├── Phase 4: Ecosystem Data (Week 10)
│   ├── deps.dev: Query dependent package counts for Python/JS/Java/Go
│   ├── Libraries.io: Query dependent counts for C++
│   └── Output: ecosystem_metrics.csv
│
├── Phase 5: Merge & Clean (Week 10)
│   ├── Merge all datasets on project_id
│   ├── Handle missing values
│   ├── Validate data quality
│   └── Output: final_dataset.csv
│
└── Phase 6: Analysis (Week 11-14)
    ├── Descriptive statistics
    ├── Hypothesis testing
    ├── Regression analysis
    └── Output: results, visualizations
```

## 4.4 Data Source Limitations & Mitigations

| Issue | Mitigation |
|-------|------------|
| **GHArchive WatchEvent/star semantics** - GitHub changed from "watch" to "star", may undercount | Cross-validate star counts with GitHub API for sample validation |
| **deps.dev → GitHub mapping** - Package names don't always map cleanly to repos | Use `repository_url` field in deps.dev; manual verification for ambiguous cases |
| **Scorecard is security-focused** - Covers CODE_OF_CONDUCT, CONTRIBUTING but not all governance aspects | Use GitHub API fallback for issue templates, PR templates, README quality |
| **Community metrics complexity** - Bus factor, contributor retention require event processing | Consider CHAOSS Augur/GrimoireLab for pre-built metrics if custom pipeline is too complex |
| **C++ ecosystem data gaps** - deps.dev doesn't support C/C++ | Use Libraries.io; acknowledge coverage may be less complete than other languages |

---

# 5. Analysis Plan

## 5.1 Analysis Methods by RQ

| RQ | Primary Analysis | Secondary Analysis | Tools |
|----|------------------|-------------------|-------|
| **RQ1** | Chi-square tests (governance practice × sustainability) | Logistic regression (multiple predictors) | Python: scipy, statsmodels |
| **RQ2** | Mann-Whitney U tests (community metrics × groups) | Cox proportional hazards (survival analysis) | Python: scipy, lifelines |
| **RQ3** | Correlation analysis (ecosystem metrics × sustainability) | Network centrality analysis | Python: scipy, networkx |
| **RQ4** | Correlation matrix (popularity vs. actual outcomes) | Predictive model comparison (AUC-ROC) | Python: sklearn, statsmodels |

## 5.2 Statistical Approach

### Descriptive Phase

- Summary statistics for all variables by group (sustainable vs. non-sustainable)
- Visualizations: boxplots, histograms, heatmaps
- Missing data analysis

### Inferential Phase

For each RQ:

1. **State hypotheses** (null and alternative)
2. **Check assumptions** (normality, homogeneity)
3. **Select appropriate test** (parametric if assumptions met, non-parametric otherwise)
4. **Calculate effect sizes** (Cohen's d, odds ratios)
5. **Apply multiple comparison corrections** (Benjamini-Hochberg)

### Practical Significance

- Focus on effect sizes, not just p-values
- Translate findings to practitioner recommendations

## 5.3 Analysis Tools

| Tool                         | Version | Purpose                   |
| ---------------------------- | ------- | ------------------------- |
| **Python**             | 3.10+   | Primary analysis language |
| **pandas**             | 2.x     | Data manipulation         |
| **numpy**              | 1.x     | Numerical operations      |
| **scipy**              | 1.x     | Statistical tests         |
| **statsmodels**        | 0.14+   | Regression analysis       |
| **lifelines**          | 0.27+   | Survival analysis         |
| **matplotlib/seaborn** | Latest  | Visualization             |
| **scikit-learn**       | 1.x     | Model comparison (RQ4)    |
| **BigQuery**           | -       | GHArchive, deps.dev, Scorecard access     |

---

# 6. Related Work (Draft v1)

## 6.1 OSS Project Success and Sustainability

**Foundational Work**:

- **Crowston & Howison (2005)** - "The Social Structure of Free and Open Source Software Development" - Established that community structure affects project outcomes
- **Chengalur-Smith et al. (2010)** - "Sustainability of FLOSS" - Early framework for OSS sustainability factors

**Project Failure Studies**:

- **Coelho & Valente (2017)** - "Why Modern Open Source Projects Fail" - Identified 8 failure patterns; we extend by examining what distinguishes survivors
- **Khondhu et al. (2013)** - "Is It All Lost? A Study of Inactive Open Source Projects" - Characterized abandonment; we add governance and community dimensions

## 6.2 Governance and Documentation

- **Fogel (2005)** - "Producing Open Source Software" - Practitioner guide establishing governance best practices
- **O'Mahony & Ferraro (2007)** - "The Emergence of Governance in an Open Source Community" - Governance evolution patterns

## 6.3 Community Health Metrics

- **Goggins & Lumbard (2021)** - "CHAOSS: Community Health Analytics in Open Source Software" - Defines standardized metrics we adopt
- **Avelino et al. (2016)** - "A Novel Approach for Estimating Truck Factors" - Bus factor measurement we adapt
- **Constantinou & Mens (2017)** - "Socio-technical evolution of the Ruby ecosystem" - Community dynamics analysis methods

## 6.4 Popularity vs. Sustainability

- **Borges et al. (2016)** - "Understanding the Factors That Impact the Popularity of GitHub Repositories" - Established popularity predictors; we test if they predict sustainability
- **Hudson et al. (2018)** - "A Survey on OSS Sustainability" - Noted disconnect between popularity and health

## 6.5 Research Gap

| Prior Work                      | Limitation                         | Our Contribution                        |
| ------------------------------- | ---------------------------------- | --------------------------------------- |
| Individual factor studies       | Examine dimensions in isolation    | Simultaneous multi-dimensional analysis |
| Popularity-focused              | Assume stars/forks indicate health | Directly validate against outcomes      |
| Qualitative governance research | Limited generalizability           | Quantitative, large-scale analysis      |
| Failure post-mortems            | Retrospective, single-case         | Comparative, controlled design          |

---

# 7. Validity Considerations

## 7.1 Construct Validity

| Threat                                    | Mitigation                                          |
| ----------------------------------------- | --------------------------------------------------- |
| "Sustainability" definition is subjective | Clear operationalization with sensitivity analysis  |
| Governance presence ≠ quality            | Acknowledge; include quality proxies where possible |
| Community metrics may be gamed            | Cross-validate with multiple indicators             |

## 7.2 Internal Validity

| Threat                | Mitigation                                                    |
| --------------------- | ------------------------------------------------------------- |
| Survivorship bias     | Match groups on initial metrics; use early-stage measurements |
| Confounding variables | Include control variables; stratify by language               |
| Temporal effects      | Restrict to 2015-2020 creation period                         |

## 7.3 External Validity

| Threat                                 | Mitigation                                               |
| -------------------------------------- | -------------------------------------------------------- |
| GitHub-specific findings               | Acknowledge; discuss generalizability to other platforms |
| Language-specific patterns             | Stratified sampling; report language-specific results    |
| Star threshold excludes small projects | Sensitivity analysis; scope findings appropriately       |

## 7.4 Reliability

| Threat                 | Mitigation                               |
| ---------------------- | ---------------------------------------- |
| Data extraction errors | Automated scripts with validation checks |
| Subjective coding      | All variables objectively measurable     |
| Replication            | Document all procedures; publish scripts |

---

# 8. Timeline

| Week         | Activities                                                                   | Deliverables                             |
| ------------ | ---------------------------------------------------------------------------- | ---------------------------------------- |
| **8**  | Finalize RQs, set up BigQuery, query GHArchive, begin sample selection | `project_sample.csv`                   |
| **9**  | Complete sampling, extract governance data, begin community data extraction  | `governance_metrics.csv`               |
| **10** | Complete community data, merge datasets, begin descriptive analysis          | `final_dataset.csv`, descriptive stats |
| **11** | Complete RQ1 analysis, begin RQ2 analysis                                    | RQ1 results                              |
| **12** | Complete RQ2 and RQ3 analysis, draft Results section                         | RQ2-3 results, Results v1                |
| **13** | Write Discussion, address validity threats                                   | Discussion v1                            |
| **14** | Complete all sections, internal review, revisions                            | Full draft                               |
| **15** | Final polishing, prepare presentation                                        | Final report, slides                     |

---

# 9. Risk Assessment

| Risk                            | Likelihood | Impact | Mitigation                                         |
| ------------------------------- | ---------- | ------ | -------------------------------------------------- |
| GHArchive data gaps         | Low        | High   | Cross-validate with GitHub API; adjust sample          |
| Sample size insufficient        | Low        | Medium | Built-in buffer (500 > minimum required)           |
| No significant findings         | Medium     | Medium | Report null results honestly; exploratory analysis |
| Time overrun on data collection | Medium     | High   | Week 8-9 buffer; prioritize RQ1-2 over RQ3         |
| Tool/library issues             | Low        | Low    | Established tools; alternatives available          |

---

# 10. Success Criteria

This study will be successful if it:

1. ✅ Answers all four RQs with statistically valid methods
2. ✅ Identifies at least 3 actionable factors for practitioners
3. ✅ Provides evidence challenging or supporting popularity-as-proxy assumption
4. ✅ Produces replicable methodology and shareable analysis code
5. ✅ Generates insights worthy of Discussion section (15% of grade)

---

*Document Version: 3.0 (Iteratively Refined)*
*Last Updated: December 25, 2025*
