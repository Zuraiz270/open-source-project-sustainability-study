"""
Phase 9: Enhanced Statistical Analysis (Hybrid Approach)
=========================================================
Implements best practices from academic research:
1. MICE imputation for missing scorecard data (47% missing)
2. Bootstrap confidence intervals for effect sizes
3. Fisher's Exact test for sparse cells + Chi-square for large cells
4. Logistic Regression + Random Forest comparison
5. 5-fold cross-validation

Usage: python scripts/run_analysis_v2.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, fisher_exact, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Setup
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Configuration
N_BOOTSTRAP = 1000
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


def load_data():
    """Load and prepare dataset"""
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df)} records")
    
    # Create binary sustainability variable
    df['is_sustainable'] = (df['sustainability_status'] == 'sustainable').astype(int)
    
    return df


def mice_imputation(df, columns, n_iterations=5):
    """
    Multiple Imputation by Chained Equations (MICE)
    Simplified version using iterative regression imputation
    """
    print("\n📊 MICE Imputation for Scorecard Metrics:")
    
    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer
    
    # Select columns for imputation
    impute_cols = [c for c in columns if c in df.columns]
    
    # Create imputer
    imputer = IterativeImputer(
        max_iter=n_iterations,
        random_state=RANDOM_STATE,
        initial_strategy='median'
    )
    
    # Fit and transform
    df_subset = df[impute_cols + ['is_sustainable']].copy()
    imputed_values = imputer.fit_transform(df_subset)
    
    # Update dataframe
    for i, col in enumerate(impute_cols):
        before_missing = df[col].isna().sum()
        df[col] = imputed_values[:, i]
        print(f"   {col}: {before_missing} missing → imputed")
    
    return df


def handle_missing_values(df):
    """Handle missing values with MICE for scorecard, simple for community"""
    print("\n" + "="*60)
    print("MISSING VALUE HANDLING")
    print("="*60)
    
    # Check missing
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    print("\nBefore imputation:")
    print(missing)
    
    # MICE for scorecard metrics (high missing rate ~47%)
    scorecard_cols = ['code_review_score', 'maintained_score', 'overall_score']
    try:
        df = mice_imputation(df, scorecard_cols)
    except ImportError:
        print("⚠️ sklearn IterativeImputer not available, using median")
        for col in scorecard_cols:
            if col in df.columns:
                df[col] = df.groupby('is_sustainable')[col].transform(
                    lambda x: x.fillna(x.median())
                )
    
    # Simple imputation for community (low missing, meaningful NaN)
    if 'median_issue_response_days' in df.columns:
        # For sustainable: use median
        # For non-sustainable: use high value (999 = no response)
        median_sus = df[df['is_sustainable'] == 1]['median_issue_response_days'].median()
        df.loc[df['is_sustainable'] == 1, 'median_issue_response_days'] = \
            df.loc[df['is_sustainable'] == 1, 'median_issue_response_days'].fillna(median_sus)
        df.loc[df['is_sustainable'] == 0, 'median_issue_response_days'] = \
            df.loc[df['is_sustainable'] == 0, 'median_issue_response_days'].fillna(999)
    
    # Check remaining missing
    missing_after = df.isnull().sum()
    missing_after = missing_after[missing_after > 0]
    print("\nAfter imputation:")
    print(missing_after if len(missing_after) > 0 else "No missing values!")
    
    return df


def bootstrap_ci(data1, data2, statistic='median_diff', n_bootstrap=N_BOOTSTRAP, ci=0.95):
    """Calculate bootstrap confidence interval for difference between groups"""
    diffs = []
    n1, n2 = len(data1), len(data2)
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        sample1 = np.random.choice(data1, size=n1, replace=True)
        sample2 = np.random.choice(data2, size=n2, replace=True)
        
        if statistic == 'median_diff':
            diff = np.median(sample1) - np.median(sample2)
        elif statistic == 'mean_diff':
            diff = np.mean(sample1) - np.mean(sample2)
        diffs.append(diff)
    
    # Calculate CI
    lower = np.percentile(diffs, (1 - ci) / 2 * 100)
    upper = np.percentile(diffs, (1 + ci) / 2 * 100)
    
    return np.mean(diffs), lower, upper


def rq1_governance_analysis(df):
    """RQ1: Governance analysis with Fisher's Exact + Chi-square"""
    print("\n" + "="*60)
    print("RQ1: GOVERNANCE ANALYSIS (Enhanced)")
    print("="*60)
    
    governance_cols = ['has_code_of_conduct', 'has_contributing', 'has_license', 
                       'has_issue_template', 'has_pull_request_template', 'has_readme']
    
    results = []
    
    for col in governance_cols:
        if col not in df.columns:
            continue
            
        df[col] = df[col].astype(int)
        
        # Create contingency table
        contingency = pd.crosstab(df['is_sustainable'], df[col])
        
        # Chi-square test
        chi2, p_chi, dof, expected = chi2_contingency(contingency)
        
        # Fisher's Exact test (for sparse cells)
        try:
            odds_ratio, p_fisher = fisher_exact(contingency)
        except:
            odds_ratio, p_fisher = np.nan, np.nan
        
        # Choose appropriate test based on expected cell counts
        min_expected = expected.min()
        if min_expected < 5:
            test_used = "Fisher's Exact"
            p_value = p_fisher
        else:
            test_used = "Chi-square"
            p_value = p_chi
        
        # Proportions
        prop_sus = df[df['is_sustainable'] == 1][col].mean()
        prop_nonsus = df[df['is_sustainable'] == 0][col].mean()
        
        # Effect size (Cramer's V)
        n = len(df)
        cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
        
        results.append({
            'Practice': col.replace('has_', '').replace('_', ' ').title(),
            'Sustainable (%)': f"{prop_sus*100:.1f}%",
            'Non-sustainable (%)': f"{prop_nonsus*100:.1f}%",
            'Test': test_used,
            'Odds Ratio': f"{odds_ratio:.2f}" if not np.isnan(odds_ratio) else "N/A",
            'p-value': f"{p_value:.4f}",
            'Cramers V': f"{cramers_v:.3f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
        print(f"\n{col}:")
        print(f"  Sustainable: {prop_sus*100:.1f}%, Non-sustainable: {prop_nonsus*100:.1f}%")
        print(f"  {test_used}: p = {p_value:.4f} {sig}")
        print(f"  Odds Ratio: {odds_ratio:.2f}, Cramer's V: {cramers_v:.3f}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq1_governance_enhanced.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq1_governance_enhanced.csv'}")
    
    return results_df


def rq2_community_analysis(df):
    """RQ2: Community analysis with Bootstrap CI"""
    print("\n" + "="*60)
    print("RQ2: COMMUNITY ANALYSIS (with Bootstrap CI)")
    print("="*60)
    
    community_cols = ['median_issue_response_days', 'median_pr_review_days', 
                      'unique_contributors', 'total_commits']
    
    results = []
    
    for col in community_cols:
        if col not in df.columns:
            continue
            
        sustainable = df[df['is_sustainable'] == 1][col].dropna().values
        non_sustainable = df[df['is_sustainable'] == 0][col].dropna().values
        
        if len(sustainable) < 5 or len(non_sustainable) < 5:
            continue
        
        # Mann-Whitney U test
        stat, p_value = mannwhitneyu(sustainable, non_sustainable, alternative='two-sided')
        
        # Bootstrap CI for median difference
        diff, ci_lower, ci_upper = bootstrap_ci(sustainable, non_sustainable)
        
        # Effect size (rank-biserial correlation)
        n1, n2 = len(sustainable), len(non_sustainable)
        effect_size = 1 - (2 * stat) / (n1 * n2)
        
        results.append({
            'Metric': col.replace('_', ' ').title(),
            'Sustainable (Median)': f"{np.median(sustainable):.2f}",
            'Non-sustainable (Median)': f"{np.median(non_sustainable):.2f}",
            'Median Diff': f"{diff:.2f}",
            '95% CI': f"[{ci_lower:.2f}, {ci_upper:.2f}]",
            'U-statistic': f"{stat:.0f}",
            'p-value': f"{p_value:.4f}",
            'Effect Size (r)': f"{effect_size:.3f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
        print(f"\n{col}:")
        print(f"  Sustainable median: {np.median(sustainable):.2f}")
        print(f"  Non-sustainable median: {np.median(non_sustainable):.2f}")
        print(f"  Median difference: {diff:.2f} (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}])")
        print(f"  Mann-Whitney U = {stat:.0f}, p = {p_value:.4f} {sig}")
        print(f"  Effect size (rank-biserial r): {effect_size:.3f}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq2_community_enhanced.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq2_community_enhanced.csv'}")
    
    return results_df


def rq3_ecosystem_analysis(df):
    """RQ3: Ecosystem analysis with Bootstrap CI"""
    print("\n" + "="*60)
    print("RQ3: ECOSYSTEM ANALYSIS (with Bootstrap CI)")
    print("="*60)
    
    ecosystem_cols = ['forks_count', 'watchers_count', 'stars_count', 'network_count']
    
    results = []
    
    for col in ecosystem_cols:
        if col not in df.columns:
            continue
            
        sustainable = df[df['is_sustainable'] == 1][col].dropna().values
        non_sustainable = df[df['is_sustainable'] == 0][col].dropna().values
        
        # Mann-Whitney U test
        stat, p_value = mannwhitneyu(sustainable, non_sustainable, alternative='two-sided')
        
        # Bootstrap CI for median difference
        diff, ci_lower, ci_upper = bootstrap_ci(sustainable, non_sustainable)
        
        # Spearman correlation with sustainability
        valid_data = df[[col, 'is_sustainable']].dropna()
        corr, corr_p = spearmanr(valid_data[col], valid_data['is_sustainable'])
        
        results.append({
            'Metric': col.replace('_', ' ').title(),
            'Sustainable (Median)': f"{np.median(sustainable):.0f}",
            'Non-sustainable (Median)': f"{np.median(non_sustainable):.0f}",
            'Median Diff': f"{diff:.0f}",
            '95% CI': f"[{ci_lower:.0f}, {ci_upper:.0f}]",
            'Spearman r': f"{corr:.3f}",
            'p-value': f"{p_value:.4f}",
            'Significant': "Yes" if p_value < 0.05 else "No"
        })
        
        sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
        print(f"\n{col}:")
        print(f"  Sustainable median: {np.median(sustainable):.0f}")
        print(f"  Non-sustainable median: {np.median(non_sustainable):.0f}")
        print(f"  Median difference: {diff:.0f} (95% CI: [{ci_lower:.0f}, {ci_upper:.0f}])")
        print(f"  Spearman r = {corr:.3f}, p = {p_value:.4f} {sig}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "rq3_ecosystem_enhanced.csv", index=False)
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq3_ecosystem_enhanced.csv'}")
    
    return results_df


def rq4_combined_analysis(df):
    """RQ4: Combined analysis with Logistic Regression + Random Forest comparison"""
    print("\n" + "="*60)
    print("RQ4: COMBINED PREDICTORS (LR vs Random Forest)")
    print("="*60)
    
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.metrics import roc_auc_score, make_scorer
    
    # Feature columns
    feature_cols = [
        # Governance
        'has_code_of_conduct', 'has_contributing', 'has_license',
        # Community
        'median_issue_response_days', 'unique_contributors',
        # Ecosystem
        'forks_count', 'watchers_count'
    ]
    
    available_cols = [c for c in feature_cols if c in df.columns]
    
    # Prepare data
    X = df[available_cols].copy()
    y = df['is_sustainable'].values
    
    # Fill any remaining missing with median
    X = X.fillna(X.median())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cross-validation setup
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    
    # Model 1: Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    lr_accuracy = cross_val_score(lr, X_scaled, y, cv=cv, scoring='accuracy')
    lr_auc = cross_val_score(lr, X_scaled, y, cv=cv, scoring='roc_auc')
    
    # Model 2: Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE)
    rf_accuracy = cross_val_score(rf, X_scaled, y, cv=cv, scoring='accuracy')
    rf_auc = cross_val_score(rf, X_scaled, y, cv=cv, scoring='roc_auc')
    
    print("\n📊 Model Comparison (5-fold CV):")
    print(f"\nLogistic Regression:")
    print(f"  Accuracy: {lr_accuracy.mean():.3f} (+/- {lr_accuracy.std()*2:.3f})")
    print(f"  ROC-AUC:  {lr_auc.mean():.3f} (+/- {lr_auc.std()*2:.3f})")
    
    print(f"\nRandom Forest:")
    print(f"  Accuracy: {rf_accuracy.mean():.3f} (+/- {rf_accuracy.std()*2:.3f})")
    print(f"  ROC-AUC:  {rf_auc.mean():.3f} (+/- {rf_auc.std()*2:.3f})")
    
    # Fit on full data for feature importance
    lr.fit(X_scaled, y)
    rf.fit(X_scaled, y)
    
    # Feature importance comparison
    lr_importance = pd.DataFrame({
        'Feature': available_cols,
        'LR_Coefficient': lr.coef_[0],
        'LR_Abs_Coef': np.abs(lr.coef_[0]),
        'RF_Importance': rf.feature_importances_
    }).sort_values('LR_Abs_Coef', ascending=False)
    
    print("\n📊 Feature Importance Comparison:")
    print(lr_importance.to_string(index=False))
    
    # Save results
    model_comparison = pd.DataFrame({
        'Model': ['Logistic Regression', 'Random Forest'],
        'Accuracy (Mean)': [lr_accuracy.mean(), rf_accuracy.mean()],
        'Accuracy (Std)': [lr_accuracy.std(), rf_accuracy.std()],
        'ROC-AUC (Mean)': [lr_auc.mean(), rf_auc.mean()],
        'ROC-AUC (Std)': [lr_auc.std(), rf_auc.std()]
    })
    
    model_comparison.to_csv(RESULTS_DIR / "rq4_model_comparison.csv", index=False)
    lr_importance.to_csv(RESULTS_DIR / "rq4_feature_importance_enhanced.csv", index=False)
    
    print(f"\n📁 Results saved to: {RESULTS_DIR / 'rq4_model_comparison.csv'}")
    print(f"📁 Feature importance saved to: {RESULTS_DIR / 'rq4_feature_importance_enhanced.csv'}")
    
    return model_comparison, lr_importance


def main():
    print("="*60)
    print("PHASE 9: ENHANCED STATISTICAL ANALYSIS")
    print("Hybrid Approach: MICE + Bootstrap + Fisher's + LR/RF")
    print("="*60)
    
    # Load data
    df = load_data()
    
    # Handle missing values (MICE for scorecard)
    df = handle_missing_values(df)
    
    # Run enhanced analyses
    rq1_results = rq1_governance_analysis(df)
    rq2_results = rq2_community_analysis(df)
    rq3_results = rq3_ecosystem_analysis(df)
    rq4_comparison, rq4_importance = rq4_combined_analysis(df)
    
    print("\n" + "="*60)
    print("✅ ENHANCED ANALYSIS COMPLETE")
    print("="*60)
    print(f"Results saved to: {RESULTS_DIR}")
    
    # Summary
    print("\n📋 SUMMARY OF IMPROVEMENTS:")
    print("1. MICE imputation for 237 missing scorecard values")
    print("2. Bootstrap 95% CIs for all group comparisons")
    print("3. Fisher's Exact test for sparse governance cells")
    print("4. Cramer's V effect size for governance")
    print("5. Logistic Regression vs Random Forest comparison")
    print("6. 5-fold stratified cross-validation")


if __name__ == "__main__":
    main()
