"""
GitHub API Data Enrichment Script
==================================
Enriches repository data with language, last commit date, and archived status.

Usage:
    1. Add your token to .env file: GITHUB_TOKEN=your_token_here
    2. python scripts/enrich_data.py
"""

import pandas as pd
import requests
import time
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "final_sample.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "enriched_sample.csv"

# GitHub API
GITHUB_API = "https://api.github.com/repos"
RATE_LIMIT_PAUSE = 0.8  # seconds between requests (stay under 5000/hour)

def get_github_token():
    """Get GitHub token from .env file"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token or token == "paste_your_token_here":
        print("❌ Error: GITHUB_TOKEN not set in .env file")
        print("\nEdit .env file and add your token:")
        print("  GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
        return None
    return token

def fetch_repo_data(owner, repo, headers):
    """Fetch repository data from GitHub API"""
    url = f"{GITHUB_API}/{owner}/{repo}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "language": data.get("language"),
                "pushed_at": data.get("pushed_at"),
                "archived": data.get("archived", False),
                "status": "success"
            }
        elif response.status_code == 404:
            return {"language": None, "pushed_at": None, "archived": None, "status": "not_found"}
        elif response.status_code == 403:
            return {"language": None, "pushed_at": None, "archived": None, "status": "rate_limited"}
        else:
            return {"language": None, "pushed_at": None, "archived": None, "status": f"error_{response.status_code}"}
    except Exception as e:
        return {"language": None, "pushed_at": None, "archived": None, "status": f"exception: {str(e)}"}

def main():
    print("=" * 60)
    print("GitHub API Data Enrichment")
    print("=" * 60)
    
    # Get token
    token = get_github_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Load data
    if not INPUT_FILE.exists():
        print(f"❌ Error: Input file not found: {INPUT_FILE}")
        return
    
    df = pd.read_csv(INPUT_FILE)
    print(f"✅ Loaded {len(df)} repositories")
    
    # Add new columns
    df["language"] = None
    df["pushed_at"] = None
    df["archived"] = None
    df["api_status"] = None
    
    # Process each repo
    total = len(df)
    success_count = 0
    
    print(f"\n🔄 Fetching data from GitHub API...")
    print(f"   Estimated time: ~{int(total * RATE_LIMIT_PAUSE / 60)} minutes\n")
    
    for idx, row in df.iterrows():
        owner = row["owner"]
        repo = row["repo"]
        
        # Fetch data
        result = fetch_repo_data(owner, repo, headers)
        
        # Update dataframe
        df.at[idx, "language"] = result["language"]
        df.at[idx, "pushed_at"] = result["pushed_at"]
        df.at[idx, "archived"] = result["archived"]
        df.at[idx, "api_status"] = result["status"]
        
        if result["status"] == "success":
            success_count += 1
        
        # Progress update
        if (idx + 1) % 100 == 0:
            print(f"   Progress: {idx + 1}/{total} ({success_count} successful)")
            
            # Save intermediate results
            df.to_csv(OUTPUT_FILE, index=False)
        
        # Rate limiting
        time.sleep(RATE_LIMIT_PAUSE)
    
    # Save final results
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Summary
    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{total}")
    print(f"📁 Output: {OUTPUT_FILE}")
    
    # Language distribution
    print("\n📊 Language Distribution:")
    lang_counts = df["language"].value_counts().head(10)
    for lang, count in lang_counts.items():
        print(f"   {lang}: {count}")

if __name__ == "__main__":
    main()
