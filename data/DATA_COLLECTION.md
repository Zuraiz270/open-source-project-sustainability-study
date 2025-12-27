# Data Collection Process

## Overview

This document describes the data collection methodology for the OSS Sustainability Study using GHArchive, BigQuery, and GitHub API.

---

## Phase 1: Initial Sample Selection ✅

### Step 1.1: BigQuery Query Execution

**Date:** December 26, 2024

**Data Source:** `githubarchive.month.202312`

**Query Purpose:** Extract candidate repositories with 100+ stars from December 2023

**Query File:** [`queries/sample_selection.sql`](queries/sample_selection.sql)

```sql
SELECT 
  repo.name as repo_name,
  COUNT(*) as stars
FROM `githubarchive.month.202312`
WHERE type = 'WatchEvent'
GROUP BY repo.name
HAVING COUNT(*) >= 100
ORDER BY stars DESC
LIMIT 2000;
```

**Results:**
- **Total repositories extracted:** 2,000
- **Data processed:** 5.41 GB
- **Star range:** 450 - 22,071

**Output File:** [`raw/project_sample_raw.csv`](raw/project_sample_raw.csv)

---

## Phase 2: Data Enrichment ✅

### Step 2.1: GitHub API Enrichment

**Date:** December 26, 2024

**Script:** [`../scripts/enrich_data.py`](../scripts/enrich_data.py)

**Data fetched:**
- Primary language
- Last commit date (`pushed_at`)
- Archived status

**Results:**
- **Total processed:** 2,000 repositories
- **Successful:** 1,955 (97.8%)
- **Errors:** 45 (repos deleted/renamed)

---

## Phase 3: Non-Sustainable Project Discovery ✅

### Step 3.1: GitHub Search for Archived/Inactive Repos

**Date:** December 27, 2024

**Script:** [`../scripts/find_archived_repos.py`](../scripts/find_archived_repos.py)

**Problem Identified:** Original trending sample (Dec 2023) had survivorship bias - mostly still-active projects.

**Solution:** Used GitHub Search API to find:
1. **Archived repos** (`archived:true stars:>=100`)
2. **Inactive repos** (`pushed:<2023-01-01 stars:>=100`)

**Search Criteria:**
- Stars ≥ 100
- Created 2015-2020
- Language: Python, TypeScript, JavaScript, Go, Java

**Results:**
- **Total non-sustainable repos found:** 831

**Output File:** [`raw/archived_repos.csv`](raw/archived_repos.csv)

---

## Phase 4: Final Balanced Sample ✅

### Step 4.1: Sample Merging

**Date:** December 27, 2024

**Script:** [`../scripts/merge_samples.py`](../scripts/merge_samples.py)

**Methodology:**
1. Sustainable projects from original trending sample (Phase 1-2)
2. Non-sustainable projects from GitHub search (Phase 3)
3. Stratified sampling: 50 sustainable + 50 non-sustainable per language

### Final Sample Composition

| Language   | Sustainable | Non-Sustainable | Total |
|------------|-------------|-----------------|-------|
| Python     | 50          | 50              | 100   |
| TypeScript | 50          | 50              | 100   |
| JavaScript | 50          | 50              | 100   |
| Go         | 50          | 50              | 100   |
| Java       | 50          | 50              | 100   |
| **Total**  | **250**     | **250**         | **500** |

**Output File:** [`processed/balanced_sample.csv`](processed/balanced_sample.csv)

---

## Phase 5: Governance Data ✅

### Step 5.1: GitHub API - Community Profile

**Date:** December 27, 2024

**Script:** [`../scripts/extract_governance.py`](../scripts/extract_governance.py)

**Endpoint:** `GET /repos/{owner}/{repo}/community/profile`

**Metrics extracted:**
- `has_code_of_conduct` (boolean)
- `has_contributing` (boolean)
- `has_license` (boolean)
- `has_readme` (boolean)
- `health_percentage` (0-100)

**Results:** 500/500 (100% coverage)

### Step 5.2: OpenSSF Scorecard - Security Metrics

**Query:** [`queries/scorecard_query.sql`](queries/scorecard_query.sql)

**Dataset:** `openssf.scorecardcron.scorecard-v2_latest` (BigQuery)

**Metrics extracted:**
- `overall_score` (0-10)
- `maintained_score` (0-10)
- `code_review_score` (0-10)

**Results:** 263/500 (53% coverage - Scorecard only covers popular projects)

**Output File:** [`processed/governance_metrics.csv`](processed/governance_metrics.csv)

---

## Phase 6: Community Data ✅

### Step 6.1: GHArchive - Community Events

**Date:** December 27, 2024

**Query:** [`queries/community_query_full.sql`](queries/community_query_full.sql)

**Dataset:** `githubarchive.month.2024*` (BigQuery - all of 2024)

**Cost:** ~€25 (4.79 TB scanned)

**Metrics extracted:**
- `median_issue_response_days` - Time to first response on issues
- `median_pr_review_days` - Time to first PR review
- `unique_contributors` - Distinct contributors in 2024
- `total_commits` - Total commits in 2024

**Results:** 500/500 repos queried (~350 have activity data, ~150 inactive)

**Output File:** [`raw/community_results.csv`](raw/community_results.csv)

---

## Phase 7: Ecosystem Data ✅

### Step 7.1: GitHub API - Ecosystem Proxies

**Date:** December 27, 2024

**Method:** GitHub API (Proxies for ecosystem importance)

**Reasoning:** External dependency data (deps.dev, Libraries.io) had insufficient coverage (0 matches) for the sample. Used GitHub native metrics as valid proxies for project impact.

**Metrics extracted:**
- `forks_count` - Derivative work (strong proxy for usage/contribution)
- `subscribers_count` (Watchers) - Active interest
- `network_count` - Total fork network size
- `stargazers_count` - Community validation (cross-reference)

**Results:** 500/500 repos queried (100% success)

**Output File:** [`processed/ecosystem_metrics.csv`](processed/ecosystem_metrics.csv)

---

## File Structure

```
data/
├── DATA_COLLECTION.md          # This documentation
├── raw/
│   ├── project_sample_raw.csv  # BigQuery export (2,000 trending repos)
│   ├── archived_repos.csv      # GitHub search (831 non-sustainable)
│   ├── scorecard_results.csv   # OpenSSF Scorecard (1.28M repos)
│   └── community_results.csv   # GHArchive community metrics
├── processed/
│   ├── balanced_sample.csv     # ✨ FINAL SAMPLE (500 projects)
│   ├── balanced_sample_stats.csv
│   ├── governance_metrics.csv  # Governance/security metrics
│   └── ecosystem_metrics.csv   # Ecosystem proxies (Stars/Forks/Watchers)
└── queries/
    ├── sample_selection.sql    # BigQuery SQL query
    ├── scorecard_query.sql     # OpenSSF Scorecard query
    └── community_query_full.sql # GHArchive community query

scripts/
├── process_sample.py           # Initial processing
├── enrich_data.py              # GitHub API enrichment  
├── find_archived_repos.py      # Find non-sustainable projects
├── merge_samples.py            # Create balanced sample
├── extract_governance.py       # Governance metrics extraction
└── extract_ecosystem.py        # Ecosystem proxies extraction
```

---

## Sustainability Classification Criteria

| Status | Definition |
|--------|------------|
| **Sustainable** | Last commit within 6 months of reference date |
| **Non-sustainable** | No commit in 18+ months OR explicitly archived |
| **Grey area** | Between 6-18 months (excluded from sample) |

---

## Data Quality Notes

1. **Star counts:** Based on WatchEvents in December 2023
2. **Sustainable projects:** From trending repos (survivorship bias acknowledged)
3. **Non-sustainable projects:** Explicitly archived or inactive since 2022
4. **Governance coverage:** GitHub API (100%), Scorecard (53%)
5. **Community coverage:** ~350/500 with activity data (inactive projects have nulls)
6. **Ecosystem coverage:** GitHub API proxies (100% - Forks/Watchers)
7. **Reference date:** December 2024

---

## ✅ Data Collection Complete

Sample selection, governance, community (Phase 6), and ecosystem (Phase 7) data collection complete. Ready for data merging.


