"""
Phase 10: Collect Missing RQ2 Metrics
======================================
Fetches bus factor and contributor diversity index for all 500 repos.

Bus Factor: Minimum number of contributors who account for ≥80% of commits
Contributor Diversity: Gini coefficient (0 = equal, 1 = one person does all)

Usage: python scripts/collect_rq2_metrics.py
"""

import os
import time
import requests
import pandas as pd
import numpy as np
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
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "rq2_metrics.csv"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_contributors(owner: str, repo: str, max_pages: int = 3) -> list:
    """Fetch top contributors for a repository."""
    contributors = []
    
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        params = {"per_page": 100, "page": page}
        
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if response.status_code == 403:
                # Rate limited
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait_time = max(reset_time - time.time(), 0) + 5
                print(f"⏳ Rate limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 404:
                return []
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            if not data:
                break
            
            contributors.extend(data)
            
            if len(data) < 100:
                break
                
        except Exception as e:
            print(f"Error fetching {owner}/{repo}: {e}")
            return []
    
    return contributors


def calculate_bus_factor(contributions: list, threshold: float = 0.8) -> int:
    """
    Calculate bus factor: minimum contributors who account for ≥threshold of commits.
    """
    if not contributions:
        return 0
    
    # Sort by contributions descending
    sorted_contrib = sorted(contributions, reverse=True)
    total = sum(sorted_contrib)
    
    if total == 0:
        return 0
    
    cumulative = 0
    bus_factor = 0
    
    for contrib in sorted_contrib:
        cumulative += contrib
        bus_factor += 1
        if cumulative / total >= threshold:
            break
    
    return bus_factor


def calculate_gini(contributions: list) -> float:
    """
    Calculate Gini coefficient for contributor diversity.
    0 = perfect equality (everyone contributes equally)
    1 = perfect inequality (one person does everything)
    """
    if not contributions or len(contributions) < 2:
        return 1.0  # Single contributor = max inequality
    
    n = len(contributions)
    sorted_contrib = sorted(contributions)
    
    # Gini formula
    cumulative = np.cumsum(sorted_contrib)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_contrib))) / (n * np.sum(sorted_contrib)) - (n + 1) / n
    
    return max(0, min(1, gini))  # Clamp to [0, 1]


def process_repository(owner: str, repo: str) -> dict:
    """Process a single repository to get bus factor and diversity index."""
    contributors = get_contributors(owner, repo)
    
    if not contributors:
        return {
            'bus_factor': None,
            'contributor_diversity_gini': None,
            'num_contributors': 0
        }
    
    # Extract contribution counts
    contributions = [c.get('contributions', 0) for c in contributors]
    
    bus_factor = calculate_bus_factor(contributions)
    gini = calculate_gini(contributions)
    
    return {
        'bus_factor': bus_factor,
        'contributor_diversity_gini': round(gini, 4),
        'num_contributors': len(contributors)
    }


def main():
    print("="*60)
    print("PHASE 10: COLLECT MISSING RQ2 METRICS")
    print("Bus Factor + Contributor Diversity Index")
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
    
    for idx, row in df.iterrows():
        owner = row['owner']
        repo = row['repo']
        
        if idx % 25 == 0:
            print(f"\n📦 Processing {idx+1}/{len(df)}: {owner}/{repo}")
        
        metrics = process_repository(owner, repo)
        metrics['repo_name'] = row['repo_name']
        results.append(metrics)
        
        # Status update
        if metrics['bus_factor']:
            print(f"   ✅ Bus factor: {metrics['bus_factor']}, Gini: {metrics['contributor_diversity_gini']:.3f}")
        
        # Rate limit protection
        if (idx + 1) % 30 == 0:
            time.sleep(2)  # Pause every 30 repos
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Merge with original data
    df_merged = df.merge(results_df, on='repo_name', how='left')
    
    # Save results
    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n📁 Saved RQ2 metrics to: {OUTPUT_FILE}")
    
    # Update final dataset
    df_merged.to_csv(DATA_FILE, index=False)
    print(f"📁 Updated final_dataset.csv with new metrics")
    
    # Summary
    valid_bus = results_df['bus_factor'].notna().sum()
    valid_gini = results_df['contributor_diversity_gini'].notna().sum()
    
    print(f"\n📊 Summary:")
    print(f"   Bus factor collected: {valid_bus}/{len(df)}")
    print(f"   Gini collected: {valid_gini}/{len(df)}")
    
    if valid_bus > 0:
        avg_bus = results_df['bus_factor'].mean()
        avg_gini = results_df['contributor_diversity_gini'].mean()
        print(f"   Average bus factor: {avg_bus:.1f}")
        print(f"   Average Gini: {avg_gini:.3f}")


if __name__ == "__main__":
    main()
