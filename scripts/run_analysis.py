"""
Phase 9: Statistical Analysis
==============================
Analyzes collected data to answer research questions about OSS sustainability.

Research Questions:
- RQ1: Governance vs Sustainability
- RQ2: Community Response Times vs Sustainability  
- RQ3: Ecosystem Metrics vs Sustainability
- RQ4: Combined Predictors

Usage: python scripts/run_analysis.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Setup
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def load_data():
    """Load and prepare dataset"""
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df)} records")
    
    # Create binary sustainability variable
    df['is_sustainable'] = (df['sustainability_status'] == 'sustainable').astype(int)
    
    return df

def handle_missing_values(df):
    """Handle missing values with appropriate strategies"""
    print("\n📊 Missing Value Analysis:")
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    print(missing)
    
    # Strategy 1: For scorecard metrics (code_review_score, maintained_score)
    # Use median imputation within sustainability group
    for col in ['code_review_score', 'maintained_score', 'overall_score']:
        if col in df.columns:
            df[col] = df.groupby('is_sustainable')[col].transform(
                lambda x: x.fillna(x.median())
            )
    
    # Strategy 2: For community metrics (median_issue_response_days)
    # Missing = no activity, impute with high value (999) or group median
    if 'median_issue_response_days' in df.columns:
        # For sustainable projects: use median
        # For non-sustainable: use high value (indicates no response)
        median_sustainable = df[df['is_sustainable'] == 1]['median_issue_response_days'].median()
        df.loc[df['is_sustainable'] == 1, 'median_issue_response_days'] = \
            df.loc[df['is_sustainable'] == 1, 'median_issue_response_days'].fillna(median_sustainable)
        df.loc[df['is_sustainable'] == 0, 'median_issue_response_days'] = \
            df.loc[df['is_sustainable'] == 0, 'median_issue_response_days'].fillna(999)
    
    print("\n✅ Missing values handled")
    return df

def rq1_governance_analysis(df):
    """RQ1: How do governance practices differ between sustainable and non-sustainable projects?"""
    print("\n" + "="*60)
    print("RQ1: GOVERNANCE ANALYSIS")
    print("="*60)
    
    governance_cols = ['has_code_of_conduct', 'has_contributing', 'has_license', 
                       'has_issue_template', 'has_pull_request_template', 'has_readme']
    
    results = []
    
    for col in governance_cols:
        if col not in df.columns:
            continue
            
        # Convert to int if boolean
        df[col] = df[col].astype(int)
        
        # Create contingency table
        contingency = pd.crosstab(df['is_sustainable'], df[col])
        
        # Chi-square test
        chi2, p_value, dof, expected = chi2_contingency(contingency)
        
        # Proportions
        prop_sustainable = df[df['is_sustainable'] == 1][col].mean()
        prop_nonsustainable = df[df['is_sustainable'] == 0][col].mean()
        
        results.append({
            'Practice': col.replace('has_', '').replace('_', ' ').title(),
            'Sustainable (%)': f"{prop_sustainable*100:.1f}%",
            'Non-sustainable (%)': f"{prop_nonsustainable*100:.1f}%",
            'Chi-square': f"{chi2:.2f}",
            'p-value': f"{p_value:.4f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        print(f"\n{col}:")
        print(f"  Sustainable: {prop_sustainable*100:.1f}%, Non-sustainable: {prop_nonsustainable*100:.1f}%")
        print(f"  Chi-square = {chi2:.2f}, p = {p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq1_governance_results.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq1_governance_results.csv'}")
    
    return results_df

def rq2_community_analysis(df):
    """RQ2: How do community response times differ between sustainable and non-sustainable projects?"""
    print("\n" + "="*60)
    print("RQ2: COMMUNITY ANALYSIS")
    print("="*60)
    
    community_cols = ['median_issue_response_days', 'median_pr_review_days', 
                      'unique_contributors', 'total_commits']
    
    results = []
    
    for col in community_cols:
        if col not in df.columns:
            continue
            
        # Get values for each group
        sustainable = df[df['is_sustainable'] == 1][col].dropna()
        non_sustainable = df[df['is_sustainable'] == 0][col].dropna()
        
        if len(sustainable) < 5 or len(non_sustainable) < 5:
            continue
        
        # Mann-Whitney U test (non-parametric)
        stat, p_value = mannwhitneyu(sustainable, non_sustainable, alternative='two-sided')
        
        # Effect size (rank-biserial correlation)
        n1, n2 = len(sustainable), len(non_sustainable)
        effect_size = 1 - (2 * stat) / (n1 * n2)
        
        results.append({
            'Metric': col.replace('_', ' ').title(),
            'Sustainable (Median)': f"{sustainable.median():.2f}",
            'Non-sustainable (Median)': f"{non_sustainable.median():.2f}",
            'U-statistic': f"{stat:.0f}",
            'p-value': f"{p_value:.4f}",
            'Effect Size': f"{effect_size:.3f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        print(f"\n{col}:")
        print(f"  Sustainable median: {sustainable.median():.2f}")
        print(f"  Non-sustainable median: {non_sustainable.median():.2f}")
        print(f"  Mann-Whitney U = {stat:.0f}, p = {p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq2_community_results.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq2_community_results.csv'}")
    
    return results_df

def rq3_ecosystem_analysis(df):
    """RQ3: How do ecosystem metrics correlate with sustainability?"""
    print("\n" + "="*60)
    print("RQ3: ECOSYSTEM ANALYSIS")
    print("="*60)
    
    ecosystem_cols = ['forks_count', 'watchers_count', 'stars_count', 'network_count']
    
    results = []
    
    for col in ecosystem_cols:
        if col not in df.columns:
            continue
            
        # Get values for each group
        sustainable = df[df['is_sustainable'] == 1][col].dropna()
        non_sustainable = df[df['is_sustainable'] == 0][col].dropna()
        
        # Mann-Whitney U test
        stat, p_value = mannwhitneyu(sustainable, non_sustainable, alternative='two-sided')
        
        # Point-biserial correlation with sustainability
        valid_data = df[[col, 'is_sustainable']].dropna()
        corr, corr_p = spearmanr(valid_data[col], valid_data['is_sustainable'])
        
        results.append({
            'Metric': col.replace('_', ' ').title(),
            'Sustainable (Median)': f"{sustainable.median():.0f}",
            'Non-sustainable (Median)': f"{non_sustainable.median():.0f}",
            'Spearman r': f"{corr:.3f}",
            'p-value': f"{p_value:.4f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        print(f"\n{col}:")
        print(f"  Sustainable median: {sustainable.median():.0f}")
        print(f"  Non-sustainable median: {non_sustainable.median():.0f}")
        print(f"  Spearman r = {corr:.3f}, p = {p_value:.4f}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq3_ecosystem_results.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq3_ecosystem_results.csv'}")
    
    return results_df

def rq4_combined_analysis(df):
    """RQ4: Which combination of factors best predicts sustainability?"""
    print("\n" + "="*60)
    print("RQ4: COMBINED PREDICTORS ANALYSIS")
    print("="*60)
    
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import classification_report
    except ImportError:
        print("⚠️ sklearn not installed. Skipping logistic regression.")
        return None
    
    # Select features
    feature_cols = [
        # Governance
        'has_code_of_conduct', 'has_contributing', 'has_license',
        # Community
        'median_issue_response_days', 'unique_contributors',
        # Ecosystem
        'forks_count', 'watchers_count'
    ]
    
    # Filter to available columns
    available_cols = [c for c in feature_cols if c in df.columns]
    
    # Prepare data
    X = df[available_cols].copy()
    y = df['is_sustainable']
    
    # Handle missing values with median
    X = X.fillna(X.median())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
    
    # Feature importance
    importance = pd.DataFrame({
        'Feature': available_cols,
        'Coefficient': model.coef_[0],
        'Abs_Coefficient': np.abs(model.coef_[0])
    }).sort_values('Abs_Coefficient', ascending=False)
    
    print("\n📊 Model Performance:")
    print(f"  Cross-validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")
    
    print("\n📊 Feature Importance (by coefficient):")
    print(importance.to_string(index=False))
    
    importance.to_csv(RESULTS_DIR / "rq4_feature_importance.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq4_feature_importance.csv'}")
    
    return importance

def main():
    print("="*60)
    print("PHASE 9: STATISTICAL ANALYSIS")
    print("="*60)
    
    # Load data
    df = load_data()
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Run analyses
    rq1_results = rq1_governance_analysis(df)
    rq2_results = rq2_community_analysis(df)
    rq3_results = rq3_ecosystem_analysis(df)
    rq4_results = rq4_combined_analysis(df)
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
    print(f"Results saved to: {RESULTS_DIR}")

if __name__ == "__main__":
    main()
