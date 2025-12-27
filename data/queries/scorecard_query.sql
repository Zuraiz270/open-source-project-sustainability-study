-- OpenSSF Scorecard Query for OSS Sustainability Study
-- Run in Google BigQuery: https://console.cloud.google.com/bigquery
-- Dataset: openssf:scorecardcron.scorecard-v2_latest
--
-- First, add the 'openssf' project to BigQuery:
-- 1. In BigQuery Explorer, click "ADD" > "Star a project by name"
-- 2. Enter: openssf
-- 3. Click "Star"

-- Query: Extract governance/security metrics for our sample repos
-- Replace the repo list with your actual repo names from balanced_sample.csv

SELECT
  repo.name as repo_name,
  date as scorecard_date,
  score as overall_score,
  
  -- Extract individual check scores
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Maintained') as maintained_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Code-Review') as code_review_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'License') as license_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Security-Policy') as security_policy_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Signed-Releases') as signed_releases_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Branch-Protection') as branch_protection_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Vulnerabilities') as vulnerabilities_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'CII-Best-Practices') as cii_best_practices_score,
  (SELECT c.score FROM UNNEST(checks) c WHERE c.name = 'Contributors') as contributors_score

FROM `openssf.scorecardcron.scorecard-v2_latest`

-- Filter to GitHub repos only and match our sample
WHERE repo.name LIKE 'github.com/%'

-- Example: Filter to specific repos (replace with your list)
-- AND REPLACE(repo.name, 'github.com/', '') IN (
--   'facebook/react',
--   'microsoft/vscode',
--   ...
-- )

ORDER BY repo.name;

-- NOTE: Export results as CSV to data/raw/scorecard_results.csv
-- Then run scripts/extract_governance.py to merge with GitHub API data
