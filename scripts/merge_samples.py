"""
Merge Samples Script
====================
Combines sustainable projects from original sample 
with non-sustainable projects from GitHub search.

Goal: Create balanced sample of ~460 projects
- 50 sustainable + 50 non-sustainable per language (Python, TS, JS, Go)
- Max available for Java
"""

import pandas as pd
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
SUSTAINABLE_FILE = BASE_DIR / "data" / "processed" / "final_400_sample.csv"
ARCHIVED_FILE = BASE_DIR / "data" / "raw" / "archived_repos.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "balanced_sample.csv"

# Target languages
TARGET_LANGUAGES = ['Python', 'TypeScript', 'JavaScript', 'Go', 'Java']
SAMPLE_PER_GROUP = 50

def load_data():
    """Load both datasets"""
    sustainable = pd.read_csv(SUSTAINABLE_FILE)
    archived = pd.read_csv(ARCHIVED_FILE)
    
    print(f"📊 Loaded sustainable sample: {len(sustainable)} repos")
    print(f"📊 Loaded archived repos: {len(archived)} repos")
    
    return sustainable, archived

def prepare_sustainable(df):
    """Filter to only sustainable projects in target languages"""
    # Filter to sustainable only
    sustainable = df[df['sustainability_status'] == 'sustainable'].copy()
    
    # Filter to target languages
    sustainable = sustainable[sustainable['language'].isin(TARGET_LANGUAGES)]
    
    print(f"\n📈 Sustainable repos in target languages: {len(sustainable)}")
    print(sustainable['language'].value_counts())
    
    return sustainable

def prepare_nonsustainable(df):
    """Filter archived repos to target languages"""
    # Filter to target languages
    nonsustainable = df[df['language'].isin(TARGET_LANGUAGES)].copy()
    
    print(f"\n📉 Non-sustainable repos in target languages: {len(nonsustainable)}")
    print(nonsustainable['language'].value_counts())
    
    return nonsustainable

def create_balanced_sample(sustainable_df, nonsustainable_df):
    """Create balanced stratified sample"""
    print("\n🎲 Creating balanced sample...")
    
    samples = []
    summary = []
    
    for lang in TARGET_LANGUAGES:
        # Sustainable for this language
        lang_sustainable = sustainable_df[sustainable_df['language'] == lang]
        available_sus = len(lang_sustainable)
        
        # Non-sustainable for this language
        lang_nonsustainable = nonsustainable_df[nonsustainable_df['language'] == lang]
        available_nonsus = len(lang_nonsustainable)
        
        # Determine sample size
        if lang == 'Java':
            # Take all available for Java (up to 50 each)
            n_sus = min(available_sus, 50)
            n_nonsus = min(available_nonsus, 50)
        else:
            n_sus = min(available_sus, SAMPLE_PER_GROUP)
            n_nonsus = min(available_nonsus, SAMPLE_PER_GROUP)
        
        # Sample sustainable
        if n_sus > 0:
            sampled_sus = lang_sustainable.sample(n=n_sus, random_state=42)
            sampled_sus = sampled_sus.copy()
            sampled_sus['sustainability_status'] = 'sustainable'
            samples.append(sampled_sus)
        
        # Sample non-sustainable
        if n_nonsus > 0:
            sampled_nonsus = lang_nonsustainable.sample(n=n_nonsus, random_state=42)
            sampled_nonsus = sampled_nonsus.copy()
            sampled_nonsus['sustainability_status'] = 'non_sustainable'
            samples.append(sampled_nonsus)
        
        summary.append({
            'language': lang,
            'sustainable_available': available_sus,
            'sustainable_sampled': n_sus,
            'nonsustainable_available': available_nonsus,
            'nonsustainable_sampled': n_nonsus,
            'total': n_sus + n_nonsus
        })
        
        print(f"   {lang}: {n_sus} sustainable + {n_nonsus} non-sustainable = {n_sus + n_nonsus}")
    
    # Combine all samples
    final_df = pd.concat(samples, ignore_index=True)
    
    # Standardize columns
    columns_to_keep = ['repo_name', 'owner', 'repo', 'stars', 'language', 
                       'pushed_at', 'archived', 'sustainability_status']
    existing_cols = [c for c in columns_to_keep if c in final_df.columns]
    final_df = final_df[existing_cols]
    
    return final_df, pd.DataFrame(summary)

def main():
    print("=" * 60)
    print("Merging Samples for Balanced Dataset")
    print("=" * 60)
    
    # Load data
    sustainable_raw, archived_raw = load_data()
    
    # Prepare datasets
    sustainable = prepare_sustainable(sustainable_raw)
    nonsustainable = prepare_nonsustainable(archived_raw)
    
    # Create balanced sample
    final_sample, summary = create_balanced_sample(sustainable, nonsustainable)
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("BALANCED SAMPLE SUMMARY")
    print("=" * 60)
    print(summary.to_string(index=False))
    print(f"\n✅ Total: {len(final_sample)} projects")
    
    # Sustainability breakdown
    print("\nBy status:")
    print(final_sample['sustainability_status'].value_counts())
    
    # Save
    final_sample.to_csv(OUTPUT_FILE, index=False)
    print(f"\n📁 Saved to: {OUTPUT_FILE}")
    
    # Save summary
    summary_file = BASE_DIR / "data" / "processed" / "balanced_sample_stats.csv"
    summary.to_csv(summary_file, index=False)
    print(f"📁 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
