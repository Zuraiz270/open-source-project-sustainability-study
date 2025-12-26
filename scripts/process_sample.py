"""
OSS Sustainability Study - Data Processing Script
==================================================
Purpose: Process BigQuery results to create final 400-project sample

Instructions:
1. Copy your downloaded CSV (bq-results-*.csv) to:
   Assignment-2/data/raw/project_sample_raw.csv

2. Run this script:
   python scripts/process_sample.py

3. Output will be saved to:
   Assignment-2/data/processed/final_sample.csv
"""

import pandas as pd
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "project_sample_raw.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "final_sample.csv"

# Target languages
TARGET_LANGUAGES = ['Python', 'JavaScript', 'Java', 'Go']

# Sample size per group per language
SAMPLE_PER_LANGUAGE = 50  # 50 * 4 languages * 2 groups = 400 total

def load_data():
    """Load the raw BigQuery export"""
    if not RAW_DATA.exists():
        print(f"❌ Error: File not found: {RAW_DATA}")
        print(f"\nPlease copy your downloaded CSV to:\n  {RAW_DATA}")
        return None
    
    df = pd.read_csv(RAW_DATA)
    print(f"✅ Loaded {len(df)} repositories from BigQuery export")
    return df

def extract_owner_repo(df):
    """Split repo.name into owner and repo"""
    if 'repo_name' in df.columns:
        df[['owner', 'repo']] = df['repo_name'].str.split('/', n=1, expand=True)
    return df

def classify_sustainability(df):
    """
    Classify projects as sustainable or non-sustainable.
    
    Note: This is a placeholder - you'll need to add last_activity data
    from another BigQuery query to properly classify.
    
    For now, we'll mark all as 'unknown' and you can update later.
    """
    # TODO: Add classification based on last commit date
    # sustainable: last commit < 6 months ago
    # non_sustainable: last commit > 18 months ago OR archived
    # grey_area: between 6-18 months (excluded)
    
    df['sustainability_status'] = 'unknown'
    return df

def create_sample(df):
    """
    Create stratified sample of 400 projects.
    
    For now, just returns top projects by stars.
    Full implementation needs GitHub API to get language info.
    """
    # Sort by stars
    df = df.sort_values('stars', ascending=False)
    
    # Take top 2000 as candidate pool
    candidates = df.head(2000).copy()
    
    print(f"\n📊 Candidate Pool Summary:")
    print(f"   Total candidates: {len(candidates)}")
    print(f"   Star range: {candidates['stars'].min()} - {candidates['stars'].max()}")
    
    return candidates

def main():
    print("=" * 60)
    print("OSS Sustainability Study - Sample Processing")
    print("=" * 60)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Process
    df = extract_owner_repo(df)
    df = classify_sustainability(df)
    candidates = create_sample(df)
    
    # Save processed data
    PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(PROCESSED_DATA, index=False)
    print(f"\n✅ Saved {len(candidates)} candidates to:")
    print(f"   {PROCESSED_DATA}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Run GitHub API queries to get:
   - Primary language for each repo
   - Last commit date
   - Archived status

2. Filter to target languages:
   Python, JavaScript, Java, Go

3. Classify sustainability:
   - Sustainable: commit in last 6 months
   - Non-sustainable: no commit in 18+ months OR archived

4. Stratified selection:
   50 per language × 2 groups = 400 total
""")

if __name__ == "__main__":
    main()
