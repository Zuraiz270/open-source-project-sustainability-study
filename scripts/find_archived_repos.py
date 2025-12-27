"""
Find Non-Sustainable (Archived) Projects
=========================================
Searches GitHub for archived repositories to balance our sample.

Uses GitHub Search API to find:
- Archived repos with 100+ stars
- Created 2015-2020
- In target languages
"""

import requests
import pandas as pd
import time
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "raw" / "archived_repos.csv"

# Target languages
TARGET_LANGUAGES = ['Python', 'TypeScript', 'JavaScript', 'Go', 'Java']

# GitHub API
GITHUB_API = "https://api.github.com"
RATE_LIMIT_PAUSE = 2  # seconds between search requests

def get_github_token():
    """Get GitHub token from .env"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token or token == "paste_your_token_here":
        print("❌ Error: GITHUB_TOKEN not set in .env file")
        return None
    return token

def search_archived_repos(language, headers, min_stars=100, per_page=100):
    """
    Search for archived repositories in a specific language.
    
    Query: archived:true stars:>=100 language:{lang} created:2015-01-01..2020-12-31
    """
    repos = []
    
    # Search query
    query = f"archived:true stars:>={min_stars} language:{language} created:2015-01-01..2020-12-31"
    
    url = f"{GITHUB_API}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page
    }
    
    print(f"\n🔍 Searching archived {language} repos...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_count", 0)
            items = data.get("items", [])
            
            print(f"   Found {total} total, retrieved {len(items)}")
            
            for item in items:
                repos.append({
                    "repo_name": item["full_name"],
                    "owner": item["owner"]["login"],
                    "repo": item["name"],
                    "stars": item["stargazers_count"],
                    "language": item.get("language"),
                    "created_at": item["created_at"],
                    "pushed_at": item["pushed_at"],
                    "archived": item["archived"],
                    "description": item.get("description", "")[:200] if item.get("description") else ""
                })
        elif response.status_code == 403:
            print(f"   ⚠️ Rate limited, waiting...")
            time.sleep(60)
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return repos

def search_inactive_repos(language, headers, min_stars=100, per_page=100):
    """
    Search for repos that haven't been pushed to since 2022.
    
    Query: stars:>=100 language:{lang} pushed:<2023-01-01 created:2015-01-01..2020-12-31
    """
    repos = []
    
    # Search for repos with last push before 2023
    query = f"stars:>={min_stars} language:{language} pushed:<2023-01-01 created:2015-01-01..2020-12-31"
    
    url = f"{GITHUB_API}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page
    }
    
    print(f"🔍 Searching inactive {language} repos (no push since 2023)...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_count", 0)
            items = data.get("items", [])
            
            print(f"   Found {total} total, retrieved {len(items)}")
            
            for item in items:
                # Skip if already archived (we got those separately)
                if not item["archived"]:
                    repos.append({
                        "repo_name": item["full_name"],
                        "owner": item["owner"]["login"],
                        "repo": item["name"],
                        "stars": item["stargazers_count"],
                        "language": item.get("language"),
                        "created_at": item["created_at"],
                        "pushed_at": item["pushed_at"],
                        "archived": item["archived"],
                        "description": item.get("description", "")[:200] if item.get("description") else ""
                    })
        elif response.status_code == 403:
            print(f"   ⚠️ Rate limited, waiting...")
            time.sleep(60)
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return repos

def main():
    print("=" * 60)
    print("Finding Non-Sustainable (Archived/Inactive) Projects")
    print("=" * 60)
    
    # Get token
    token = get_github_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    all_repos = []
    
    # Search for archived and inactive repos in each language
    for lang in TARGET_LANGUAGES:
        # Archived repos
        archived = search_archived_repos(lang, headers)
        all_repos.extend(archived)
        time.sleep(RATE_LIMIT_PAUSE)
        
        # Inactive repos (no push since 2023)
        inactive = search_inactive_repos(lang, headers)
        all_repos.extend(inactive)
        time.sleep(RATE_LIMIT_PAUSE)
    
    # Create DataFrame
    df = pd.DataFrame(all_repos)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['repo_name'])
    
    # Add sustainability status
    df['sustainability_status'] = 'non_sustainable'
    
    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"✅ Total non-sustainable repos found: {len(df)}")
    print(f"\nBy language:")
    print(df['language'].value_counts())
    print(f"\n📁 Saved to: {OUTPUT_FILE}")
    
    print("\n🔜 Next: Run enrich_archived.py to get full metadata")

if __name__ == "__main__":
    main()
