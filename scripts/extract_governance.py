"""
Governance Data Extraction Script
==================================
Extracts governance metrics for all 500 projects using:
1. OpenSSF Scorecard (from BigQuery export) - primary source
2. GitHub API community profile - fallback for missing repos

Metrics extracted:
- has_code_of_conduct, has_contributing, has_license, has_readme
- scorecard_score, maintained_score, code_review_score, etc.
"""

import pandas as pd
import requests
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.parent
SAMPLE_FILE = BASE_DIR / "data" / "processed" / "balanced_sample.csv"
SCORECARD_FILE = BASE_DIR / "data" / "raw" / "scorecard_results.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "governance_metrics.csv"

GITHUB_API = "https://api.github.com"
RATE_LIMIT_PAUSE = 0.5  # seconds between API calls

def get_github_token():
    """Get GitHub token from .env"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token or token == "paste_your_token_here":
        print("⚠️ Warning: GITHUB_TOKEN not set, API calls may be rate limited")
        return None
    return token

def load_sample():
    """Load the balanced sample"""
    df = pd.read_csv(SAMPLE_FILE)
    print(f"✅ Loaded {len(df)} projects from balanced sample")
    return df

def load_scorecard_data():
    """Load OpenSSF Scorecard data if available"""
    if SCORECARD_FILE.exists():
        df = pd.read_csv(SCORECARD_FILE)
        # Normalize repo names (remove github.com/ prefix)
        if 'repo_name' in df.columns:
            df['repo_name'] = df['repo_name'].str.replace('github.com/', '', regex=False)
        print(f"✅ Loaded {len(df)} Scorecard results")
        return df
    else:
        print(f"⚠️ Scorecard file not found: {SCORECARD_FILE}")
        print("   Run the BigQuery query first and save results to this file")
        return None

def get_community_profile(owner, repo, headers):
    """
    Get community profile from GitHub API.
    Returns governance file presence.
    
    Endpoint: GET /repos/{owner}/{repo}/community/profile
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/community/profile"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', {})
            
            return {
                'has_code_of_conduct': files.get('code_of_conduct') is not None,
                'has_contributing': files.get('contributing') is not None,
                'has_license': files.get('license') is not None,
                'has_readme': files.get('readme') is not None,
                'has_issue_template': files.get('issue_template') is not None,
                'has_pull_request_template': files.get('pull_request_template') is not None,
                'health_percentage': data.get('health_percentage', 0),
                'api_status': 'success'
            }
        elif response.status_code == 404:
            return {'api_status': 'not_found'}
        else:
            return {'api_status': f'error_{response.status_code}'}
            
    except Exception as e:
        return {'api_status': f'exception_{str(e)[:50]}'}

def extract_governance_from_api(sample_df, headers):
    """Extract governance data for all repos using GitHub API"""
    print("\n🔄 Fetching governance data from GitHub API...")
    
    results = []
    total = len(sample_df)
    
    for idx, row in sample_df.iterrows():
        owner = row['owner']
        repo = row['repo']
        
        if idx % 50 == 0:
            print(f"   Progress: {idx}/{total} ({idx*100//total}%)")
        
        profile = get_community_profile(owner, repo, headers)
        profile['repo_name'] = row['repo_name']
        profile['owner'] = owner
        profile['repo'] = repo
        
        results.append(profile)
        time.sleep(RATE_LIMIT_PAUSE)
    
    return pd.DataFrame(results)

def merge_with_scorecard(api_df, scorecard_df):
    """Merge GitHub API data with Scorecard data"""
    if scorecard_df is None:
        print("ℹ️ No Scorecard data to merge")
        return api_df
    
    # Merge on repo_name
    merged = api_df.merge(
        scorecard_df[['repo_name', 'overall_score', 'maintained_score', 
                      'code_review_score', 'license_score', 'security_policy_score']],
        on='repo_name',
        how='left'
    )
    
    scorecard_matches = merged['overall_score'].notna().sum()
    print(f"✅ Merged Scorecard data: {scorecard_matches}/{len(merged)} repos matched")
    
    return merged

def main():
    print("=" * 60)
    print("Governance Data Extraction")
    print("=" * 60)
    
    # Get token
    token = get_github_token()
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Load sample
    sample_df = load_sample()
    
    # Load Scorecard data if available
    scorecard_df = load_scorecard_data()
    
    # Extract governance data from GitHub API
    api_df = extract_governance_from_api(sample_df, headers)
    
    # Merge with Scorecard data
    final_df = merge_with_scorecard(api_df, scorecard_df)
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    success = (final_df['api_status'] == 'success').sum()
    print(f"✅ Successful API calls: {success}/{len(final_df)}")
    
    print("\nGovernance file presence:")
    for col in ['has_code_of_conduct', 'has_contributing', 'has_license', 'has_readme']:
        if col in final_df.columns:
            count = final_df[col].sum() if final_df[col].dtype == bool else final_df[col].fillna(False).sum()
            print(f"   {col}: {count} ({count*100//len(final_df)}%)")
    
    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n📁 Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
