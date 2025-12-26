-- Sample Selection Query for OSS Sustainability Study
-- Run in Google BigQuery: https://console.cloud.google.com/bigquery
-- 
-- Purpose: Extract candidate projects for sustainability analysis
-- Output: ~2000 candidate projects to filter down to 400 sample

-- Step 1: Count stars per repo (using 2023 data as baseline)
WITH star_counts AS (
  SELECT 
    repo.name as repo_name,
    COUNT(*) as stars
  FROM `githubarchive.month.2023*`
  WHERE type = 'WatchEvent'
  GROUP BY repo.name
  HAVING COUNT(*) >= 100
),

-- Step 2: Get repo metadata (language, creation date, fork status)
repo_info AS (
  SELECT DISTINCT
    repo.name as repo_name,
    JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.language') as language,
    TIMESTAMP(JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.created_at')) as created_at
  FROM `githubarchive.month.202312`
  WHERE type = 'PullRequestEvent'
    AND JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.fork') = 'false'
),

-- Step 3: Get last activity date per repo
last_activity AS (
  SELECT 
    repo.name as repo_name,
    MAX(created_at) as last_push_date
  FROM `githubarchive.month.2025*`
  WHERE type = 'PushEvent'
  GROUP BY repo.name
)

-- Step 4: Join all data and classify sustainability
SELECT 
  s.repo_name,
  s.stars,
  r.language,
  r.created_at,
  l.last_push_date,
  CASE 
    WHEN l.last_push_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 MONTH) 
    THEN 'sustainable'
    WHEN l.last_push_date < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 18 MONTH) 
         OR l.last_push_date IS NULL
    THEN 'non_sustainable'
    ELSE 'grey_area'  -- Excluded from final sample
  END as sustainability_status
FROM star_counts s
LEFT JOIN repo_info r ON s.repo_name = r.repo_name
LEFT JOIN last_activity l ON s.repo_name = l.repo_name
WHERE r.language IN ('Python', 'JavaScript', 'Java', 'Go')
  AND r.created_at BETWEEN '2015-01-01' AND '2020-12-31'
ORDER BY s.stars DESC
LIMIT 5000;
