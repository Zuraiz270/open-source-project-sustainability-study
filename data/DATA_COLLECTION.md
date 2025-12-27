# Data Collection Process

## Overview

This document describes the data collection methodology for the OSS Sustainability Study using GHArchive and BigQuery.

---

## Phase 1: Initial Sample Selection

### Step 1.1: BigQuery Query Execution

**Date:** December 26, 2024

**Data Source:** `bigquery-public-data.github_repos` and `githubarchive.month.202312`

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
- **Cost:** $0 (within free tier)
- **Star range:** 450 - 22,071

**Output File:** [`raw/project_sample_raw.csv`](raw/project_sample_raw.csv)

---

## Phase 2: Initial Data Processing ✅

### Step 2.1: Python Processing Script

**Status:** ✅ Completed (December 26, 2024)

**Script:** [`../scripts/process_sample.py`](../scripts/process_sample.py)

**Operations performed:**
1. Loaded raw CSV from BigQuery export
2. Split `repo_name` into `owner` and `repo` columns
3. Added `sustainability_status` column (placeholder: "unknown")
4. Created candidate pool of 2,000 repositories

**Output File:** [`processed/final_sample.csv`](processed/final_sample.csv)

**Output Columns:**
| Column | Description |
|--------|-------------|
| `repo_name` | Full repository name (owner/repo) |
| `stars` | Star count from WatchEvents in Dec 2023 |
| `owner` | GitHub organization/user |
| `repo` | Repository name |
| `sustainability_status` | Classification (pending enrichment) |

---

## Phase 3: Data Enrichment ✅

### Step 3.1: GitHub API Enrichment

**Status:** ✅ Completed (December 26, 2024)

**Script:** [`../scripts/enrich_data.py`](../scripts/enrich_data.py)

**Data fetched from GitHub API:**
- Primary language
- Last commit date (`pushed_at`)
- Archived status

**Results:**
- **Total processed:** 2,000 repositories
- **Successful:** 1,955 (97.8%)
- **Not found/errors:** 45

**Output File:** [`processed/enriched_sample.csv`](processed/enriched_sample.csv)

**Language Distribution (Top 10):**
| Language | Count |
|----------|-------|
| Python | 460 |
| TypeScript | 292 |
| JavaScript | 145 |
| Go | 135 |
| Rust | 114 |
| C++ | 99 |
| Jupyter Notebook | 75 |
| Java | 68 |
| C | 55 |
| C# | 47 |

### Step 3.2: Sustainability Classification

**Criteria:**
- **Sustainable:** Last commit within 6 months
- **Non-sustainable:** No commit in 18+ months OR archived
- **Grey area (excluded):** Between 6-18 months

---

## Phase 4: Final Sample Selection (Pending)

### Step 4.1: Language Filtering

Filter to target languages only:
- Python
- JavaScript  
- Java
- Go

### Step 4.2: Stratified Sampling

**Target sample size:** 400 repositories
- 50 sustainable per language × 4 languages = 200
- 50 non-sustainable per language × 4 languages = 200

**Output:** `processed/final_400_sample.csv`

---

## File Structure

```
data/
├── DATA_COLLECTION.md     # This documentation
├── raw/
│   └── project_sample_raw.csv   # BigQuery export (2,000 repos)
├── processed/
│   └── final_sample.csv         # Processed candidates
└── queries/
    └── sample_selection.sql     # BigQuery SQL queries
```

---

## Data Quality Notes

1. **Star counts:** Based on WatchEvents in December 2023 only
2. **Repository status:** Not validated against current GitHub state
3. **Language:** Not yet extracted (requires enrichment)
4. **Sustainability:** Not yet classified (requires last commit date)

---

## Next Steps

- [ ] Enrich data with language and last commit information
- [ ] Filter to target languages
- [ ] Classify sustainability status
- [ ] Perform stratified sampling
- [ ] Validate final 400-sample dataset
