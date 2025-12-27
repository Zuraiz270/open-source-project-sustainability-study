"""
Fill Missing Community Data Script (Phase 8b)
==============================================
Uses GitHub API to fetch issue response times for repos
that have NULL median_issue_response_days in final_dataset.csv.

This fills the gap from GHArchive (which only had 2024 data for active repos).
"""

import pandas as pd
import requests
import time
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
FINAL_DATASET = DATA_DIR / "final_dataset.csv"
OUTPUT_FILE = DATA_DIR / "community_filled.csv"

# GitHub API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_issue_response_time(owner, repo, max_issues=20):
    """
    Fetch recent issues and calculate median time to first response.
    Returns median response time in days, or None if no issues/responses.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {
        "state": "all",
        "per_page": max_issues,
        "sort": "created",
        "direction": "desc"
    }
    
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if resp.status_code == 404:
            return None, "repo_not_found"
        elif resp.status_code == 403:
            # Rate limit
            reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(reset_time - time.time(), 60)
            print(f"   ⚠️ Rate limit hit. Sleeping {sleep_time:.0f}s...")
            time.sleep(sleep_time)
            return get_issue_response_time(owner, repo, max_issues)  # Retry
        elif resp.status_code != 200:
            return None, f"error_{resp.status_code}"
        
        issues = resp.json()
        
        if not issues:
            return None, "no_issues"
        
        response_times = []
        
        for issue in issues:
            # Skip pull requests (they appear in issues endpoint)
            if "pull_request" in issue:
                continue
            
            created_at = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            
            # Get first comment (response)
            comments_url = issue["comments_url"]
            comments_resp = requests.get(
                comments_url, 
                headers=HEADERS, 
                params={"per_page": 1},
                timeout=10
            )
            
            if comments_resp.status_code == 200:
                comments = comments_resp.json()
                if comments:
                    first_comment_at = datetime.fromisoformat(
                        comments[0]["created_at"].replace("Z", "+00:00")
                    )
                    response_time = (first_comment_at - created_at).total_seconds() / 86400  # days
                    response_times.append(response_time)
        
        if response_times:
            median = sorted(response_times)[len(response_times) // 2]
            return median, "success"
        else:
            return None, "no_responses"
            
    except Exception as e:
        return None, f"exception: {str(e)}"


def main():
    print("="*60)
    print("PHASE 8b: FILL MISSING COMMUNITY DATA")
    print("="*60)
    
    # Load dataset
    df = pd.read_csv(FINAL_DATASET)
    print(f"✅ Loaded {len(df)} records from final_dataset.csv")
    
    # Find repos with missing median_issue_response_days
    missing_mask = df["median_issue_response_days"].isna()
    missing_df = df[missing_mask].copy()
    print(f"📊 Found {len(missing_df)} repos with missing issue response data")
    
    if len(missing_df) == 0:
        print("✅ No missing data to fill!")
        return
    
    # Process each repo
    results = []
    for idx, row in missing_df.iterrows():
        owner = row["owner"]
        repo = row["repo"]
        print(f"   [{len(results)+1}/{len(missing_df)}] {owner}/{repo}...", end=" ")
        
        response_time, status = get_issue_response_time(owner, repo)
        
        if response_time is not None:
            print(f"✓ {response_time:.2f} days")
        else:
            print(f"- {status}")
        
        results.append({
            "repo_name": row["repo_name"],
            "owner": owner,
            "repo": repo,
            "filled_median_issue_response_days": response_time,
            "fill_status": status
        })
        
        # Rate limiting (5000 requests/hour = ~1.4/sec, be conservative)
        time.sleep(0.5)
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Merge back
    filled_count = results_df["filled_median_issue_response_days"].notna().sum()
    print(f"\n📊 Filled {filled_count}/{len(missing_df)} repos with issue response data")
    
    # Update original dataframe
    for _, result_row in results_df.iterrows():
        if pd.notna(result_row["filled_median_issue_response_days"]):
            mask = df["repo_name"] == result_row["repo_name"]
            df.loc[mask, "median_issue_response_days"] = result_row["filled_median_issue_response_days"]
    
    # Save updated dataset
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n📁 Saved updated dataset to: {OUTPUT_FILE}")
    
    # Summary
    still_missing = df["median_issue_response_days"].isna().sum()
    print(f"\n📊 Summary:")
    print(f"   - Originally missing: {len(missing_df)}")
    print(f"   - Filled: {filled_count}")
    print(f"   - Still missing: {still_missing}")


if __name__ == "__main__":
    main()
