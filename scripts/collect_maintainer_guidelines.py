"""
Phase 11: Collect Maintainer Guidelines Metric
===============================================
Checks for presence of maintainer/governance files:
- MAINTAINERS.md (or MAINTAINERS)
- GOVERNANCE.md
- CODEOWNERS

If any of these exist → has_maintainer_guidelines = 1

Usage: python scripts/collect_maintainer_guidelines.py
"""

import os
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file")

# Setup
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Files to check
GOVERNANCE_FILES = [
    "MAINTAINERS.md",
    "MAINTAINERS",
    "GOVERNANCE.md",
    "GOVERNANCE",
    "CODEOWNERS",
    ".github/CODEOWNERS"
]


def check_file_exists(owner: str, repo: str, filepath: str) -> bool:
    """Check if a file exists in the repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.status_code == 200
    except:
        return False


def check_maintainer_guidelines(owner: str, repo: str) -> dict:
    """Check for presence of maintainer/governance files."""
    found_files = []
    
    for filepath in GOVERNANCE_FILES:
        if check_file_exists(owner, repo, filepath):
            found_files.append(filepath)
    
    has_guidelines = len(found_files) > 0
    
    return {
        'has_maintainer_guidelines': 1 if has_guidelines else 0,
        'governance_files_found': ','.join(found_files) if found_files else None
    }


def main():
    print("="*60)
    print("PHASE 11: COLLECT MAINTAINER GUIDELINES")
    print("MAINTAINERS.md, GOVERNANCE.md, CODEOWNERS")
    print("="*60)
    
    # Load dataset
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df)} repositories")
    
    # Check rate limit
    rate_response = requests.get("https://api.github.com/rate_limit", headers=HEADERS)
    if rate_response.status_code == 200:
        remaining = rate_response.json()['rate']['remaining']
        print(f"📊 API rate limit remaining: {remaining}")
    
    # Process each repository
    results = []
    found_count = 0
    
    for idx, row in df.iterrows():
        owner = row['owner']
        repo = row['repo']
        
        if idx % 50 == 0:
            print(f"\n📦 Processing {idx+1}/{len(df)}: {owner}/{repo}")
        
        metrics = check_maintainer_guidelines(owner, repo)
        metrics['repo_name'] = row['repo_name']
        results.append(metrics)
        
        if metrics['has_maintainer_guidelines']:
            found_count += 1
            if metrics['governance_files_found']:
                print(f"   ✅ Found: {metrics['governance_files_found']}")
        
        # Rate limit protection - we make up to 6 API calls per repo
        if (idx + 1) % 20 == 0:
            time.sleep(1)
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Merge with original data
    df_merged = df.merge(results_df[['repo_name', 'has_maintainer_guidelines']], on='repo_name', how='left')
    
    # Save updated dataset
    df_merged.to_csv(DATA_FILE, index=False)
    print(f"\n📁 Updated final_dataset.csv")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Repos with maintainer guidelines: {found_count}/{len(df)} ({found_count/len(df)*100:.1f}%)")
    
    # Quick analysis
    if 'is_sustainable' not in df_merged.columns:
        df_merged['is_sustainable'] = (df_merged['sustainability_status'] == 'sustainable').astype(int)
    
    sus = df_merged[df_merged['is_sustainable'] == 1]['has_maintainer_guidelines'].mean()
    nonsus = df_merged[df_merged['is_sustainable'] == 0]['has_maintainer_guidelines'].mean()
    
    print(f"\n📈 Quick Analysis:")
    print(f"   Sustainable with guidelines: {sus*100:.1f}%")
    print(f"   Non-sustainable with guidelines: {nonsus*100:.1f}%")


if __name__ == "__main__":
    main()
