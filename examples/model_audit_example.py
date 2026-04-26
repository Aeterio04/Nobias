"""
Example: Model Audit - Fairness auditing for trained ML models

This example demonstrates how to audit a trained model for bias and fairness violations.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Import model audit
import sys
sys.path.insert(0, '../library')
from model_audit import audit_model, quick_audit


def create_synthetic_hiring_data(n_samples=2000):
    """Create synthetic hiring dataset with potential bias."""
    np.random.seed(42)
    
    # Protected attributes
    gender = np.random.choice(['Male', 'Female'], n_samples, p=[0.6, 0.4])
    race = np.random.choice(['White', 'Black', 'Asian', 'Hispanic'], n_samples, 
                           p=[0.6, 0.15, 0.15, 0.10])
    
    # Features
    years_experience = np.random.exponential(5, n_samples)
    education_level = np.random.choice([1, 2, 3, 4], n_samples, p=[0.1, 0.3, 0.4, 0.2])
    interview_score = np.random.normal(70, 15, n_samples)
    
    # Create biased target (hired)
    # Base probability on legitimate factors
    base_score = (
        years_experience * 2 +
        education_level * 5 +
        interview_score * 0.3
    )
    
    # Add bias: favor males and white candidates
    bias_score = base_score.copy()
    bias_score[gender == 'Male'] += 10
    bias_score[race == 'White'] += 8
    
    # Convert to binary outcome
    threshold = np.percentile(bias_score, 70)
    hired = (bias_score > threshold).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'gender': gender,
        'race': race,
        'years_experience': years_experience,
        'education_level': education_level,
        'interview_score': interview_score,
        'hired': hired,
    })
    
    return df


def example_basic_audit():
    """Example 1: Basic model audit."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Model Audit")
    print("=" * 80)
    
    # Create synthetic data
    print("\n1. Creating synthetic hiring dataset...")
    df = create_synthetic_hiring_data(n_samples=2000)
    print(f"   Dataset size: {len(df)}")
    print(f"   Hired rate: {df['hired'].mean():.2%}")
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)
    
    # Train a model (intentionally including protected attributes)
    print("\n2. Training RandomForest model...")
    X_train = train_df.drop('hired', axis=1)
    y_train = train_df['hired']
    
    # Convert categorical to numeric
    X_train_encoded = pd.get_dummies(X_train, columns=['gender', 'race'])
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_encoded, y_train)
    
    # Prepare test data
    X_test = test_df.drop('hired', axis=1)
    y_test = test_df['hired']
    X_test_encoded = pd.get_dummies(X_test, columns=['gender', 'race'])
    
    # Ensure same columns
    for col in X_train_encoded.columns:
        if col not in X_test_encoded.columns:
            X_test_encoded[col] = 0
    X_test_encoded = X_test_encoded[X_train_encoded.columns]
    
    # Add protected attributes back for auditing
    X_test_with_protected = X_test_encoded.copy()
    X_test_with_protected['gender'] = X_test['gender'].values
    X_test_with_protected['race'] = X_test['race'].values
    
    # Save test data
    test_data_path = 'test_hiring_data.csv'
    test_df_for_audit = X_test_with_protected.copy()
    test_df_for_audit['hired'] = y_test.values
    test_df_for_audit.to_csv(test_data_path, index=False)
    
    print(f"   Model accuracy: {accuracy_score(y_test, model.predict(X_test_encoded)):.4f}")
    
    # Run audit
    print("\n3. Running fairness audit...")
    report = audit_model(
        model=model,
        test_data=test_data_path,
        protected_attributes=['gender', 'race'],
        target_column='hired',
        positive_value=1,
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)
    print(report)
    
    # Export report
    print("\n4. Exporting report...")
    report.export("hiring_model_audit.json", format="json")
    report.export("hiring_model_audit.txt", format="text")
    print("   ✓ Reports saved")
    
    return report


def example_quick_audit():
    """Example 2: Quick audit with in-memory data."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Quick Audit (In-Memory)")
    print("=" * 80)
    
    # Create data
    df = create_synthetic_hiring_data(n_samples=1000)
    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)
    
    # Train model
    X_train = train_df.drop('hired', axis=1)
    y_train = train_df['hired']
    X_train_encoded = pd.get_dummies(X_train, columns=['gender', 'race'])
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train_encoded, y_train)
    
    # Prepare test data
    X_test = test_df.drop('hired', axis=1)
    y_test = test_df['hired']
    X_test_encoded = pd.get_dummies(X_test, columns=['gender', 'race'])
    
    for col in X_train_encoded.columns:
        if col not in X_test_encoded.columns:
            X_test_encoded[col] = 0
    X_test_encoded = X_test_encoded[X_train_encoded.columns]
    
    # Add protected attributes back
    X_test_encoded['gender'] = X_test['gender'].values
    X_test_encoded['race'] = X_test['race'].values
    
    # Quick audit
    print("\nRunning quick audit...")
    report = quick_audit(
        model=model,
        X_test=X_test_encoded,
        y_test=y_test,
        protected_attributes=['gender', 'race'],
        positive_value=1,
    )
    
    print("\nQuick Audit Summary:")
    print(f"  Overall Severity: {report.overall_severity.value}")
    print(f"  Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
    print(f"  Critical Findings: {len(report.get_critical_findings())}")
    
    return report


def example_detailed_analysis(report):
    """Example 3: Detailed analysis of audit results."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Detailed Analysis")
    print("=" * 80)
    
    # Analyze scorecard
    print("\n1. Fairness Scorecard:")
    print("-" * 80)
    for metric_name, result in report.scorecard.items():
        status = "✓" if result.passed else "✗"
        print(f"  {status} {result.metric_name}: {result.value:.4f}")
    
    # Analyze counterfactual results
    print("\n2. Counterfactual Analysis:")
    print("-" * 80)
    cf = report.counterfactual_result
    print(f"  Total comparisons: {cf.total_comparisons:,}")
    print(f"  Total flips: {cf.total_flips:,}")
    print(f"  Flip rate: {cf.flip_rate:.2%}")
    print("\n  Flips by attribute:")
    for attr, count in cf.flips_by_attribute.items():
        rate = cf.flip_rates_by_attribute[attr]
        print(f"    {attr}: {count:,} ({rate:.2%})")
    
    print("\n  Top flip examples:")
    for i, example in enumerate(cf.top_flip_examples[:3], 1):
        print(f"    {i}. {example}")
    
    # Analyze findings
    print("\n3. Key Findings:")
    print("-" * 80)
    for finding in report.findings[:5]:
        print(f"  [{finding.severity.value}] {finding.title}")
        print(f"    {finding.description}")
        print(f"    Affected: {', '.join(finding.affected_groups)}")
        print()
    
    # Analyze mitigation options
    print("4. Mitigation Recommendations:")
    print("-" * 80)
    for i, mitigation in enumerate(report.mitigation_options, 1):
        retrain = " (requires retraining)" if mitigation.requires_retraining else ""
        print(f"  {i}. {mitigation.strategy_name} [{mitigation.category}]{retrain}")
        print(f"     {mitigation.description}")
        print(f"     Expected impact: {mitigation.expected_impact}")
        print(f"     Complexity: {mitigation.implementation_complexity}")
        print()
    
    # Intersectional findings
    if report.intersectional_findings:
        print("5. Intersectional Findings:")
        print("-" * 80)
        for finding in report.intersectional_findings[:3]:
            print(f"  {finding}")


if __name__ == "__main__":
    # Run examples
    report1 = example_basic_audit()
    report2 = example_quick_audit()
    example_detailed_analysis(report1)
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - hiring_model_audit.json")
    print("  - hiring_model_audit.txt")
    print("  - test_hiring_data.csv")
