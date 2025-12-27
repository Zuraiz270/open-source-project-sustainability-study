"""
Final Sample Selection Script
=============================
Classifies sustainability and creates stratified sample.

Steps:
1. Load enriched data
2. Classify sustainability (6/18 month thresholds)
3. Filter to target languages
4. Stratified sampling (50+50 per language, max for Java)
5. Output final sample
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from dateutil import parser

# Configuration
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "enriched_sample.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "final_400_sample.csv"
STATS_FILE = BASE_DIR / "data" / "processed" / "sample_statistics.csv"

# Target languages
TARGET_LANGUAGES = ['Python', 'TypeScript', 'JavaScript', 'Go', 'Java']

# Thresholds (in months)
SUSTAINABLE_THRESHOLD = 6       # Last commit within 6 months = sustainable
NON_SUSTAINABLE_THRESHOLD = 18  # No commit in 18+ months = non-sustainable

# Sample size per group per language (except Java)
SAMPLE_PER_GROUP = 50

# Reference date for calculations (December 2024)
REFERENCE_DATE = datetime(2024, 12, 26, tzinfo=timezone.utc)

def load_data():
    """Load enriched sample data"""
    if not INPUT_FILE.exists():
        print(f"❌ Error: Input file not found: {INPUT_FILE}")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    print(f"✅ Loaded {len(df)} repositories")
    return df

def parse_date(date_str):
    """Parse ISO date string to datetime"""
    if pd.isna(date_str) or date_str == "" or date_str is None:
        return None
    try:
        return parser.parse(date_str)
    except:
        return None

def months_since(date, reference=REFERENCE_DATE):
    """Calculate months between date and reference"""
    if date is None:
        return None
    
    # Ensure date is timezone-aware
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    
    delta = reference - date
    return delta.days / 30.44  # Average days per month

def classify_sustainability(df):
    """
    Classify projects based on last commit and archived status.
    
    Sustainable: Last commit within 6 months
    Non-sustainable: No commit in 18+ months OR archived
    Grey area: Between 6-18 months (excluded from sample)
    """
    print("\n📊 Classifying sustainability...")
    
    # Parse dates and calculate months since last push
    df['pushed_date'] = df['pushed_at'].apply(parse_date)
    df['months_inactive'] = df['pushed_date'].apply(months_since)
    
    # Classification logic
    def classify(row):
        # If archived, it's non-sustainable
        if row['archived'] == True:
            return 'non_sustainable'
        
        # If no push date, can't classify
        if pd.isna(row['months_inactive']):
            return 'unknown'
        
        months = row['months_inactive']
        
        if months <= SUSTAINABLE_THRESHOLD:
            return 'sustainable'
        elif months >= NON_SUSTAINABLE_THRESHOLD:
            return 'non_sustainable'
        else:
            return 'grey_area'
    
    df['sustainability_status'] = df.apply(classify, axis=1)
    
    # Print classification summary
    print("\n📈 Classification Summary:")
    status_counts = df['sustainability_status'].value_counts()
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    return df

def filter_languages(df):
    """Filter to target languages only"""
    print(f"\n🔍 Filtering to target languages: {TARGET_LANGUAGES}")
    
    df_filtered = df[df['language'].isin(TARGET_LANGUAGES)].copy()
    
    print(f"   Before: {len(df)} repos")
    print(f"   After: {len(df_filtered)} repos")
    
    # Language breakdown
    print("\n📊 Language breakdown (after filtering):")
    lang_status = df_filtered.groupby(['language', 'sustainability_status']).size().unstack(fill_value=0)
    print(lang_status)
    
    return df_filtered

def stratified_sample(df):
    """
    Create stratified sample:
    - 50 sustainable + 50 non-sustainable per language
    - For Java: take all available (max)
    """
    print("\n🎲 Creating stratified sample...")
    
    samples = []
    
    for lang in TARGET_LANGUAGES:
        lang_df = df[df['language'] == lang]
        
        for status in ['sustainable', 'non_sustainable']:
            status_df = lang_df[lang_df['sustainability_status'] == status]
            available = len(status_df)
            
            # Determine sample size
            if lang == 'Java':
                n_sample = min(available, available)  # Take all available for Java
            else:
                n_sample = min(available, SAMPLE_PER_GROUP)
            
            # Random sample
            if n_sample > 0:
                sampled = status_df.sample(n=n_sample, random_state=42)
                samples.append(sampled)
                print(f"   {lang} - {status}: {n_sample}/{available}")
            else:
                print(f"   {lang} - {status}: 0/{available} ⚠️")
    
    # Combine all samples
    final_df = pd.concat(samples, ignore_index=True)
    
    print(f"\n✅ Final sample size: {len(final_df)}")
    
    return final_df

def save_results(df, stats_df):
    """Save final sample and statistics"""
    # Save final sample
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n📁 Saved final sample to: {OUTPUT_FILE}")
    
    # Save statistics
    stats_df.to_csv(STATS_FILE, index=False)
    print(f"📁 Saved statistics to: {STATS_FILE}")

def main():
    print("=" * 60)
    print("Final Sample Selection")
    print("=" * 60)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Step 3.2: Classify sustainability
    df = classify_sustainability(df)
    
    # Step 4.1: Filter to target languages
    df_filtered = filter_languages(df)
    
    # Exclude grey area
    df_eligible = df_filtered[df_filtered['sustainability_status'].isin(['sustainable', 'non_sustainable'])]
    print(f"\n📊 Eligible repos (excluding grey area): {len(df_eligible)}")
    
    # Step 4.2: Stratified sampling
    final_sample = stratified_sample(df_eligible)
    
    # Generate statistics
    stats = final_sample.groupby(['language', 'sustainability_status']).size().reset_index(name='count')
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SAMPLE SUMMARY")
    print("=" * 60)
    summary = final_sample.groupby(['language', 'sustainability_status']).size().unstack(fill_value=0)
    print(summary)
    print(f"\nTotal: {len(final_sample)} projects")
    
    # Save results
    save_results(final_sample, stats)
    
    print("\n✅ Phase 4 Complete!")

if __name__ == "__main__":
    main()
