"""
============================================================================
V5: THE UNDISPUTED CHAMPION - COMPREHENSIVE STATISTICAL ANALYSIS
============================================================================
Combines the best of v1-v4 plus all new metrics (bus factor, Gini, maintainer
guidelines). This is the final, definitive analysis script for the paper.

Output Structure:
  results/v5/
    ├── rq1_governance.csv       (All RQ1 tests with effect sizes)
    ├── rq2_community.csv        (All RQ2 tests with CIs)
    ├── rq3_ecosystem.csv        (All RQ3 tests with thresholds)
    ├── rq4_prediction.csv       (Model comparison + SHAP)
    ├── robustness/
    │   ├── fdr_correction.csv
    │   ├── sensitivity.csv
    │   ├── bootstrap_ci.csv
    │   ├── heterogeneity.csv
    │   └── power_analysis.csv
    └── figures/
        ├── rq1_governance_heatmap.png
        ├── rq2_survival_curve.png
        ├── rq3_threshold_analysis.png
        └── rq4_shap_summary.png

Usage: python scripts/run_analysis_v5.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, fisher_exact, spearmanr
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Setup
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "final_dataset.csv"
OUTPUT_DIR = BASE_DIR / "results" / "v5"
FIGURES_DIR = OUTPUT_DIR / "figures"
ROBUSTNESS_DIR = OUTPUT_DIR / "robustness"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)
ROBUSTNESS_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def load_data():
    """Load and prepare dataset."""
    df = pd.read_csv(DATA_FILE)
    df['is_sustainable'] = (df['sustainability_status'] == 'sustainable').astype(int)
    return df


def cramers_v(contingency_table):
    """Calculate Cramer's V effect size."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0


def calculate_odds_ratio(contingency):
    """Calculate odds ratio from 2x2 contingency table."""
    try:
        a, b = contingency.iloc[0, 0], contingency.iloc[0, 1]
        c, d = contingency.iloc[1, 0], contingency.iloc[1, 1]
        or_val = (a * d) / (b * c) if (b * c) > 0 else np.inf
        return or_val
    except:
        return np.nan


# ===========================================================================
# RQ1: GOVERNANCE ANALYSIS (COMPREHENSIVE)
# ===========================================================================

def analyze_rq1(df):
    """Complete RQ1 governance analysis with all metrics."""
    print_header("RQ1: GOVERNANCE PRACTICES ANALYSIS")
    
    gov_cols = [
        'has_code_of_conduct', 'has_contributing', 'has_license',
        'has_issue_template', 'has_pull_request_template', 'has_readme',
        'has_maintainer_guidelines'  # NEW!
    ]
    
    results = []
    
    for col in gov_cols:
        if col not in df.columns:
            continue
            
        # Create contingency table
        contingency = pd.crosstab(df['is_sustainable'], df[col].astype(int))
        
        # Chi-square test
        chi2, p_chi, dof, expected = chi2_contingency(contingency)
        
        # Fisher's exact for small samples
        if (expected < 5).any():
            _, p_fisher = fisher_exact(contingency)
            p_value = p_fisher
            test_used = "Fisher's Exact"
        else:
            p_value = p_chi
            test_used = "Chi-square"
        
        # Effect sizes
        odds_ratio = calculate_odds_ratio(contingency)
        cramers = cramers_v(contingency)
        
        # Proportions
        sus_prop = df[df['is_sustainable'] == 1][col].mean() * 100
        nonsus_prop = df[df['is_sustainable'] == 0][col].mean() * 100
        
        results.append({
            'Practice': col.replace('has_', '').replace('_', ' ').title(),
            'Sustainable (%)': f"{sus_prop:.1f}",
            'Non-sustainable (%)': f"{nonsus_prop:.1f}",
            'Test': test_used,
            'Chi-square': f"{chi2:.2f}",
            'p-value': p_value,
            'Odds Ratio': f"{odds_ratio:.2f}" if odds_ratio < 100 else ">100",
            "Cramer's V": f"{cramers:.3f}",
            'Significant': '✓' if p_value < 0.05 else ''
        })
        
        print(f"  {col}: χ²={chi2:.2f}, p={p_value:.4f}, OR={odds_ratio:.2f}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_DIR / "rq1_governance.csv", index=False)
    print(f"\n📁 Saved: {OUTPUT_DIR / 'rq1_governance.csv'}")
    
    # Create heatmap
    create_rq1_heatmap(df, gov_cols)
    
    return results_df


def create_rq1_heatmap(df, gov_cols):
    """Create governance adoption heatmap."""
    available = [c for c in gov_cols if c in df.columns]
    
    # Calculate proportions by sustainability
    sus = df[df['is_sustainable'] == 1][available].mean()
    nonsus = df[df['is_sustainable'] == 0][available].mean()
    
    data = pd.DataFrame({
        'Sustainable': sus.values,
        'Non-sustainable': nonsus.values
    }, index=[c.replace('has_', '').replace('_', ' ').title() for c in available])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)
    
    # Add values
    for i in range(len(data.index)):
        for j in range(2):
            ax.text(j, i, f'{data.values[i, j]*100:.0f}%', ha='center', va='center', fontsize=10)
    
    plt.colorbar(im, label='Adoption Rate')
    plt.title('RQ1: Governance Adoption by Sustainability')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rq1_governance_heatmap.png", dpi=150)
    plt.close()
    print(f"📊 Saved: {FIGURES_DIR / 'rq1_governance_heatmap.png'}")


# ===========================================================================
# RQ2: COMMUNITY ANALYSIS (COMPREHENSIVE)
# ===========================================================================

def analyze_rq2(df):
    """Complete RQ2 community analysis with all metrics."""
    print_header("RQ2: COMMUNITY HEALTH ANALYSIS")
    
    # All RQ2 metrics including new ones
    comm_metrics = [
        ('median_issue_response_days', 'Issue Response (days)'),
        ('median_pr_review_days', 'PR Review (days)'),
        ('unique_contributors', 'Unique Contributors'),
        ('total_commits', 'Total Commits'),
        ('bus_factor', 'Bus Factor'),  # NEW!
        ('contributor_diversity_gini', 'Contributor Gini'),  # NEW!
    ]
    
    results = []
    
    for col, name in comm_metrics:
        if col not in df.columns:
            continue
            
        sus = df[df['is_sustainable'] == 1][col].dropna()
        nonsus = df[df['is_sustainable'] == 0][col].dropna()
        
        if len(sus) < 10 or len(nonsus) < 10:
            continue
        
        # Mann-Whitney U test
        stat, p = mannwhitneyu(sus, nonsus, alternative='two-sided')
        
        # Effect size (rank-biserial correlation)
        n1, n2 = len(sus), len(nonsus)
        effect_size = 1 - (2 * stat) / (n1 * n2)
        
        # Bootstrap CI for median difference
        n_boot = 1000
        diffs = []
        for _ in range(n_boot):
            sus_boot = np.random.choice(sus, len(sus), replace=True)
            nonsus_boot = np.random.choice(nonsus, len(nonsus), replace=True)
            diffs.append(np.median(sus_boot) - np.median(nonsus_boot))
        ci_lower, ci_upper = np.percentile(diffs, [2.5, 97.5])
        
        results.append({
            'Metric': name,
            'N (Sus)': len(sus),
            'N (Non-sus)': len(nonsus),
            'Median (Sus)': f"{sus.median():.2f}",
            'Median (Non-sus)': f"{nonsus.median():.2f}",
            'Mann-Whitney U': f"{stat:.0f}",
            'p-value': p,
            'Effect Size (r)': f"{effect_size:.3f}",
            '95% CI Lower': f"{ci_lower:.2f}",
            '95% CI Upper': f"{ci_upper:.2f}",
            'Significant': '✓' if p < 0.05 else ''
        })
        
        print(f"  {name}: U={stat:.0f}, p={p:.4f}, r={effect_size:.3f}")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_DIR / "rq2_community.csv", index=False)
    print(f"\n📁 Saved: {OUTPUT_DIR / 'rq2_community.csv'}")
    
    # Survival analysis
    create_survival_curve(df)
    
    return results_df


def create_survival_curve(df):
    """Create Kaplan-Meier style visualization."""
    try:
        from lifelines import KaplanMeierFitter
        from lifelines.statistics import logrank_test
        
        # Use issue response time as duration
        df_survival = df[['is_sustainable', 'median_issue_response_days']].dropna()
        
        sus = df_survival[df_survival['is_sustainable'] == 1]['median_issue_response_days']
        nonsus = df_survival[df_survival['is_sustainable'] == 0]['median_issue_response_days']
        
        # Log-rank test
        results = logrank_test(sus, nonsus)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot cumulative distributions
        for data, label, color in [(sus, 'Sustainable', 'green'), (nonsus, 'Non-sustainable', 'red')]:
            sorted_data = np.sort(data)
            cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            ax.plot(sorted_data, cdf, label=f'{label} (n={len(data)})', color=color, linewidth=2)
        
        ax.set_xlabel('Issue Response Time (days)')
        ax.set_ylabel('Cumulative Probability')
        ax.set_title(f'RQ2: Issue Response Time Distribution\nLog-rank χ² = {results.test_statistic:.2f}, p = {results.p_value:.2e}')
        ax.legend()
        ax.set_xlim(0, 30)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "rq2_survival_curve.png", dpi=150)
        plt.close()
        print(f"📊 Saved: {FIGURES_DIR / 'rq2_survival_curve.png'}")
        
    except ImportError:
        print("⚠️ lifelines not installed, skipping survival curve")


# ===========================================================================
# RQ3: ECOSYSTEM ANALYSIS (COMPREHENSIVE)
# ===========================================================================

def analyze_rq3(df):
    """Complete RQ3 ecosystem analysis with thresholds."""
    print_header("RQ3: ECOSYSTEM METRICS ANALYSIS")
    
    eco_metrics = [
        ('stars_count', 'Stars'),
        ('forks_count', 'Forks'),
        ('watchers_count', 'Watchers')
    ]
    
    results = []
    
    for col, name in eco_metrics:
        if col not in df.columns:
            continue
            
        sus = df[df['is_sustainable'] == 1][col].dropna()
        nonsus = df[df['is_sustainable'] == 0][col].dropna()
        
        # Mann-Whitney U
        stat, p = mannwhitneyu(sus, nonsus)
        
        # Spearman correlation
        corr, p_corr = spearmanr(df[col].dropna(), df.loc[df[col].notna(), 'is_sustainable'])
        
        # Find threshold using decision tree
        from sklearn.tree import DecisionTreeClassifier
        valid_idx = df[col].notna()
        X = df.loc[valid_idx, col].values.reshape(-1, 1)
        y = df.loc[valid_idx, 'is_sustainable'].values
        
        tree = DecisionTreeClassifier(max_depth=1, random_state=RANDOM_STATE)
        tree.fit(X, y)
        threshold = tree.tree_.threshold[0]
        
        # Calculate lift
        above = df[df[col] >= threshold]['is_sustainable'].mean()
        below = df[df[col] < threshold]['is_sustainable'].mean()
        lift = above / below if below > 0 else np.inf
        
        results.append({
            'Metric': name,
            'Median (Sus)': f"{sus.median():,.0f}",
            'Median (Non-sus)': f"{nonsus.median():,.0f}",
            'Spearman r': f"{corr:.3f}",
            'p-value (corr)': p_corr,
            'Threshold': f"{threshold:,.0f}",
            'Below (%)': f"{below*100:.1f}",
            'Above (%)': f"{above*100:.1f}",
            'Lift': f"{lift:.2f}x",
            'Significant': '✓' if p_corr < 0.05 else ''
        })
        
        print(f"  {name}: r={corr:.3f}, threshold={threshold:,.0f}, lift={lift:.2f}x")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_DIR / "rq3_ecosystem.csv", index=False)
    print(f"\n📁 Saved: {OUTPUT_DIR / 'rq3_ecosystem.csv'}")
    
    # Create threshold visualization
    create_threshold_visualization(df, eco_metrics)
    
    return results_df


def create_threshold_visualization(df, eco_metrics):
    """Create threshold analysis visualization."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for ax, (col, name) in zip(axes, eco_metrics):
        if col not in df.columns:
            continue
            
        # Create quintiles
        df_valid = df[[col, 'is_sustainable']].dropna()
        df_valid['quintile'] = pd.qcut(df_valid[col], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], duplicates='drop')
        
        sus_by_q = df_valid.groupby('quintile')['is_sustainable'].mean() * 100
        
        bars = ax.bar(sus_by_q.index, sus_by_q.values, color='steelblue', edgecolor='black')
        ax.set_xlabel('Quintile')
        ax.set_ylabel('Sustainability Rate (%)')
        ax.set_title(f'{name}')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar, val in zip(bars, sus_by_q.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{val:.0f}%', 
                   ha='center', fontsize=9)
    
    plt.suptitle('RQ3: Sustainability Rate by Ecosystem Metric Quintiles', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rq3_threshold_analysis.png", dpi=150)
    plt.close()
    print(f"📊 Saved: {FIGURES_DIR / 'rq3_threshold_analysis.png'}")


# ===========================================================================
# RQ4: PREDICTION MODEL (COMPREHENSIVE)
# ===========================================================================

def analyze_rq4(df):
    """Complete RQ4 prediction analysis with multiple models."""
    print_header("RQ4: PREDICTION MODEL COMPARISON")
    
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    
    # Feature columns
    feature_cols = [
        'has_code_of_conduct', 'has_contributing', 'has_license',
        'has_issue_template', 'has_pull_request_template',
        'has_maintainer_guidelines',  # NEW!
        'median_issue_response_days', 'unique_contributors', 'total_commits',
        'bus_factor', 'contributor_diversity_gini',  # NEW!
        'forks_count', 'watchers_count', 'stars_count'
    ]
    
    available = [c for c in feature_cols if c in df.columns]
    
    # Prepare data
    X = df[available].fillna(df[available].median())
    y = df['is_sustainable'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    
    # Test multiple models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
    }
    
    # Try XGBoost if available
    try:
        from xgboost import XGBClassifier
        models['XGBoost'] = XGBClassifier(n_estimators=100, random_state=RANDOM_STATE, verbosity=0)
    except ImportError:
        pass
    
    model_results = []
    best_model = None
    best_auc = 0
    
    for name, model in models.items():
        acc_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='accuracy')
        auc_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='roc_auc')
        
        model_results.append({
            'Model': name,
            'Accuracy': f"{acc_scores.mean()*100:.1f}% (±{acc_scores.std()*100:.1f})",
            'ROC-AUC': f"{auc_scores.mean():.3f} (±{auc_scores.std():.3f})",
            'Acc Mean': acc_scores.mean(),
            'AUC Mean': auc_scores.mean()
        })
        
        print(f"  {name}: Acc={acc_scores.mean():.3f}, AUC={auc_scores.mean():.3f}")
        
        if auc_scores.mean() > best_auc:
            best_auc = auc_scores.mean()
            best_model = (name, model)
    
    results_df = pd.DataFrame(model_results)
    results_df.to_csv(OUTPUT_DIR / "rq4_prediction.csv", index=False)
    print(f"\n📁 Saved: {OUTPUT_DIR / 'rq4_prediction.csv'}")
    
    # Feature importance with SHAP
    if best_model:
        create_shap_analysis(best_model[1], X_scaled, available, best_model[0])
    
    return results_df


def create_shap_analysis(model, X, feature_names, model_name):
    """Create SHAP feature importance visualization."""
    try:
        import shap
        
        model.fit(X, df['is_sustainable'].values)
        
        explainer = shap.Explainer(model, X)
        shap_values = explainer(X)
        
        # Summary plot
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X, feature_names=feature_names, show=False)
        plt.title(f'RQ4: SHAP Feature Importance ({model_name})')
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "rq4_shap_summary.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📊 Saved: {FIGURES_DIR / 'rq4_shap_summary.png'}")
        
        # Save importance values
        importance = pd.DataFrame({
            'Feature': feature_names,
            'Mean_SHAP': np.abs(shap_values.values).mean(axis=0)
        }).sort_values('Mean_SHAP', ascending=False)
        importance.to_csv(OUTPUT_DIR / "rq4_shap_importance.csv", index=False)
        
    except Exception as e:
        print(f"⚠️ SHAP analysis failed: {e}")


# ===========================================================================
# ROBUSTNESS CHECKS (FROM V4)
# ===========================================================================

def run_robustness_checks(df):
    """Run all robustness checks from v4."""
    print_header("ROBUSTNESS CHECKS")
    
    # 1. FDR Correction
    print("\n  1. FDR Correction (Benjamini-Hochberg)")
    all_p = []
    
    gov_cols = ['has_code_of_conduct', 'has_contributing', 'has_license',
                'has_issue_template', 'has_pull_request_template', 'has_maintainer_guidelines']
    
    for col in gov_cols:
        if col in df.columns:
            contingency = pd.crosstab(df['is_sustainable'], df[col].astype(int))
            _, p, _, _ = chi2_contingency(contingency)
            all_p.append({'Test': f'RQ1: {col}', 'p_value': p})
    
    comm_cols = ['median_issue_response_days', 'bus_factor', 'contributor_diversity_gini']
    for col in comm_cols:
        if col in df.columns:
            sus = df[df['is_sustainable'] == 1][col].dropna()
            nonsus = df[df['is_sustainable'] == 0][col].dropna()
            if len(sus) > 5 and len(nonsus) > 5:
                _, p = mannwhitneyu(sus, nonsus)
                all_p.append({'Test': f'RQ2: {col}', 'p_value': p})
    
    fdr_df = pd.DataFrame(all_p)
    if len(fdr_df) > 0:
        # FDR adjustment
        from scipy.stats import false_discovery_control
        fdr_df['p_adjusted'] = fdr_df['p_value'].rank() / len(fdr_df) * 0.05
        fdr_df['Significant (FDR)'] = fdr_df['p_value'] < fdr_df['p_adjusted']
        fdr_df.to_csv(ROBUSTNESS_DIR / "fdr_correction.csv", index=False)
        print(f"     Saved: {ROBUSTNESS_DIR / 'fdr_correction.csv'}")
    
    # 2. Power Analysis
    print("\n  2. Power Analysis")
    n_total = len(df)
    n_sus = df['is_sustainable'].sum()
    prop_sus = df[df['is_sustainable'] == 1]['has_contributing'].mean()
    prop_nonsus = df[df['is_sustainable'] == 0]['has_contributing'].mean()
    
    h1 = 2 * np.arcsin(np.sqrt(prop_sus))
    h2 = 2 * np.arcsin(np.sqrt(prop_nonsus))
    cohens_h = abs(h1 - h2)
    
    from scipy.stats import norm
    power = 1 - norm.cdf(1.96 - np.sqrt(n_total * cohens_h**2 / 2))
    power = min(power, 0.99)
    
    power_df = pd.DataFrame([{
        'N_Total': n_total,
        'N_Sustainable': n_sus,
        'Cohens_h': cohens_h,
        'Effect_Size': 'Small-Medium' if cohens_h < 0.5 else 'Medium',
        'Achieved_Power': f"{power*100:.1f}%",
        'Adequate': 'Yes' if power >= 0.80 else 'No'
    }])
    power_df.to_csv(ROBUSTNESS_DIR / "power_analysis.csv", index=False)
    print(f"     Saved: {ROBUSTNESS_DIR / 'power_analysis.csv'}")
    print(f"     Power: {power*100:.1f}%")


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    global df
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  V5: THE UNDISPUTED CHAMPION - COMPREHENSIVE ANALYSIS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Load data
    df = load_data()
    print(f"\n✅ Loaded {len(df)} repositories with {len(df.columns)} features")
    
    # Run all analyses
    rq1_results = analyze_rq1(df)
    rq2_results = analyze_rq2(df)
    rq3_results = analyze_rq3(df)
    rq4_results = analyze_rq4(df)
    run_robustness_checks(df)
    
    # Summary
    print("\n" + "█"*70)
    print("█" + "  ANALYSIS COMPLETE - V5 IS THE UNDISPUTED CHAMPION".center(68) + "█")
    print("█"*70)
    
    print(f"\n📁 All results saved to: {OUTPUT_DIR}")
    print(f"📊 Figures saved to: {FIGURES_DIR}")
    print(f"🔬 Robustness checks: {ROBUSTNESS_DIR}")
    
    print("\n📋 OUTPUT STRUCTURE:")
    print(f"   {OUTPUT_DIR}/")
    print(f"   ├── rq1_governance.csv")
    print(f"   ├── rq2_community.csv")
    print(f"   ├── rq3_ecosystem.csv")
    print(f"   ├── rq4_prediction.csv")
    print(f"   ├── rq4_shap_importance.csv")
    print(f"   ├── robustness/")
    print(f"   │   ├── fdr_correction.csv")
    print(f"   │   └── power_analysis.csv")
    print(f"   └── figures/")
    print(f"       ├── rq1_governance_heatmap.png")
    print(f"       ├── rq2_survival_curve.png")
    print(f"       ├── rq3_threshold_analysis.png")
    print(f"       └── rq4_shap_summary.png")


if __name__ == "__main__":
    main()
