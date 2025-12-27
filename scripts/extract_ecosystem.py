"""
Ecosystem Data Extraction via GitHub API (Option B)
Extracts ecosystem proxies: Forks and Watchers (Subscribers)

Source: GitHub API
Metrics:
- forks_count: Proxy for derivative work/usage
- subscribers_count: Watchers (proxy for interest)
- stargazers_count: Stars (validation)

Input: data/processed/balanced_sample.csv
Output: data/processed/ecosystem_metrics.csv
"""
import pandas as pd
import requests
import time
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SAMPLE_FILE = BASE_DIR / "data" / "processed" / "balanced_sample.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "ecosystem_metrics.csv"

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
} if GITHUB_TOKEN else {}

def get_repo_metrics(owner, repo):
    """Get forks and watchers from GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'forks_count': data.get('forks_count', 0),
                'watchers_count': data.get('subscribers_count', 0), # 'watchers' in UI is 'subscribers_count' in API
                'stars_count': data.get('stargazers_count', 0),
                'network_count': data.get('network_count', 0) # Total forks including hierarchy
            }
        elif resp.status_code == 404:
            return None
        elif resp.status_code == 403:
            print("   ⚠️ Rate limit exceeded. Waiting 60s...")
            time.sleep(60)
            return get_repo_metrics(owner, repo)
        else:
            print(f"   ⚠️ Error {resp.status_code} for {owner}/{repo}")
            return None
    except Exception as e:
        print(f"   ⚠️ Exception for {owner}/{repo}: {e}")
        return None

def main():
    print("=" * 60)
    print("Ecosystem Data Extraction (GitHub API Proxies)")
    print("=" * 60)
    
    if not GITHUB_TOKEN:
        print("⚠️ Warning: No GITHUB_TOKEN found. Rate limits will be low (60/hr).")
    
    # Load sample
    df = pd.read_csv(SAMPLE_FILE)
    print(f"✅ Loaded {len(df)} projects from balanced sample")
    
    results = []
    total = len(df)
    success_count = 0
    
    print(f"\n🔄 Fetching Forks & Watchers from GitHub...")
    
    for idx, row in df.iterrows():
        owner = row['owner']
        repo = row['repo']
        repo_name = row['repo_name']
        
        result = {
            'repo_name': repo_name,
            'owner': owner,
            'repo': repo,
            'forks_count': None,
            'watchers_count': None,
            'stars_count': None,
            'network_count': None,
            'status': 'error'
        }
        
        metrics = get_repo_metrics(owner, repo)
        
        if metrics:
            result.update(metrics)
            result['status'] = 'success'
            success_count += 1
        
        results.append(result)
        
        # Progress
        if (idx + 1) % 50 == 0 or idx == total - 1:
            print(f"   Progress: {idx + 1}/{total} ({(idx + 1) * 100 // total}%) - Success: {success_count}")
        
        # Friendly rate limiting
        time.sleep(0.1)
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Save
    results_df.to_csv(OUTPUT_FILE, index=False)
    
    # Summary
    print(f"\n✅ Done! {success_count}/{total} repos processed")
    print(f"📁 Saved to: {OUTPUT_FILE}")
    
    # Stats
    success_df = results_df[results_df['status'] == 'success']
    if not success_df.empty:
        print(f"\nTop 5 by Forks:")
        print(success_df.nlargest(5, 'forks_count')[['repo_name', 'forks_count']])
        print(f"\nTop 5 by Watchers:")
        print(success_df.nlargest(5, 'watchers_count')[['repo_name', 'watchers_count']])

if __name__ == "__main__":
    main()
