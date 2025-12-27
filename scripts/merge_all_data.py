"""
Merge All Data Script (Phase 8)
===============================
Merges all collected datasets into a final dataset for analysis.

Inputs:
1. balanced_sample.csv (Base: 500 projects)
2. governance_metrics.csv (Scorecard + GitHub API)
3. community_results.csv (GHArchive metrics)
4. ecosystem_metrics.csv (Forks/Watchers)

Output:
- data/processed/final_dataset.csv
"""

import pandas as pd
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"

def main():
    print("="*60)
    print("PHASE 8: MERGING DATASETS")
    print("="*60)

    # 1. Load Base Sample
    sample_path = PROCESSED_DIR / "balanced_sample.csv"
    df = pd.read_csv(sample_path)
    print(f"✅ Loaded Base Sample: {len(df)} records")
    
    # 2. Load Governance Data
    gov_path = PROCESSED_DIR / "governance_metrics.csv"
    if gov_path.exists():
        gov_df = pd.read_csv(gov_path)
        print(f"✅ Loaded Governance Data: {len(gov_df)} records")
        
        # Merge (Left Join)
        # Assuming common column 'repo_name'
        cols_to_use = gov_df.columns.difference(df.columns).tolist()
        cols_to_use.append('repo_name')
        df = df.merge(gov_df[cols_to_use], on='repo_name', how='left')
    else:
        print("⚠️ Governance data missing!")

    # 3. Load Community Data
    comm_path = RAW_DIR / "community_results.csv"
    if comm_path.exists():
        comm_df = pd.read_csv(comm_path)
        print(f"✅ Loaded Community Data: {len(comm_df)} records")
        
        # Merge
        cols_to_use = comm_df.columns.difference(df.columns).tolist()
        cols_to_use.append('repo_name')
        df = df.merge(comm_df[cols_to_use], on='repo_name', how='left')
    else:
        print("⚠️ Community data missing!")

    # 4. Load Ecosystem Data
    eco_path = PROCESSED_DIR / "ecosystem_metrics.csv"
    if eco_path.exists():
        eco_df = pd.read_csv(eco_path)
        print(f"✅ Loaded Ecosystem Data: {len(eco_df)} records")
        
        # Merge
        cols_to_use = eco_df.columns.difference(df.columns).tolist()
        cols_to_use.append('repo_name')
        df = df.merge(eco_df[cols_to_use], on='repo_name', how='left')
    else:
        print("⚠️ Ecosystem data missing!")

    # 5. Final Checks
    print("\nData Quality Check:")
    print(f"Total Rows: {len(df)}")
    print(f"Missing Values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    
    # Save
    out_path = PROCESSED_DIR / "final_dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"\n📁 Saved Final Dataset to: {out_path}")

if __name__ == "__main__":
    main()
