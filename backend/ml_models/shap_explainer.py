"""
SHAP-based Model Explainability for Credit Scoring
Provides transparent explanations for credit decisions
"""

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class CreditScoreExplainer:
    """
    SHAP explainer for credit risk model
    """
    
    def __init__(self, model, training_data: pd.DataFrame = None):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained XGBoost model
            training_data: Background training data for SHAP (sample of training set)
        """
        self.model = model
        
        # Create SHAP explainer
        if training_data is not None:
            # Use a sample for faster computation
            background = shap.sample(training_data, min(100, len(training_data)))
            self.explainer = shap.TreeExplainer(model, background)
        else:
            self.explainer = shap.TreeExplainer(model)
    
    def explain_prediction(self, X: pd.DataFrame, 
                          feature_names: List[str] = None,
                          top_n: int = 10) -> Dict:
        """
        Generate SHAP explanation for a prediction
        
        Returns:
            Dictionary with:
            - shap_values: SHAP values for all features
            - feature_contributions: Top N feature contributions
            - base_value: Base prediction value
            - predicted_value: Actual predicted value
        """
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # For binary classification, shap_values might be a list
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Get values for positive class
        
        # Get base value (expected value)
        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[1]  # Positive class base value
        
        # Get predicted value
        predicted_proba = self.model.predict_proba(X)[0, 1]
        
        # Create feature contributions
        contributions = []
        feature_names = feature_names or X.columns.tolist()
        
        for i, (feature, shap_val, feature_val) in enumerate(
            zip(feature_names, shap_values[0], X.iloc[0].values)
        ):
            contributions.append({
                'feature': feature,
                'feature_value': float(feature_val),
                'shap_value': float(shap_val),
                'impact': 'positive' if shap_val > 0 else 'negative'
            })
        
        # Sort by absolute SHAP value
        contributions.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        # Convert SHAP values to credit score impact
        contributions_with_score = self._shap_to_score_impact(
            contributions[:top_n], 
            base_value, 
            predicted_proba
        )
        
        result = {
            'base_value': float(base_value),
            'predicted_probability': float(predicted_proba),
            'feature_contributions': contributions_with_score,
            'explanation_text': self._generate_explanation_text(contributions_with_score)
        }
        
        return result
    
    def _shap_to_score_impact(self, contributions: List[Dict], 
                             base_value: float, 
                             predicted_proba: float) -> List[Dict]:
        """
        Convert SHAP values to credit score point impacts
        """
        # Total SHAP sum should equal predicted - base
        total_shap = sum(c['shap_value'] for c in contributions)
        
        # Map probability change to score change
        # Probability range 0-1 maps to score range 300-1000 (700 points)
        score_range = 700
        
        for contrib in contributions:
            # Contribution to probability
            prob_contribution = contrib['shap_value']
            
            # Convert to score points
            score_points = prob_contribution * score_range
            
            contrib['score_impact'] = round(score_points)
            contrib['impact_text'] = self._format_impact_text(
                contrib['feature'], 
                contrib['score_impact'],
                contrib['feature_value']
            )
        
        return contributions
    
    def _format_impact_text(self, feature: str, 
                           score_impact: int, 
                           feature_value: float) -> str:
        """
        Format human-readable impact text
        """
        # Feature name mapping to readable text
        feature_map = {
            'overall_payment_score': 'Payment History',
            'income_stability_score': 'Income Stability',
            'digital_footprint_score': 'Digital Activity',
            'utility_payment_regularity': 'Utility Payments',
            'upi_transaction_count_monthly': 'UPI Transactions',
            'monthly_income': 'Monthly Income',
            'loan_to_income_ratio': 'Loan-to-Income Ratio',
            'debt_to_income_ratio': 'Debt-to-Income Ratio',
            'education_level': 'Education Level',
            'years_at_current_address': 'Address Stability',
            'gst_filing_regularity': 'GST Filing Record',
            'business_vintage_years': 'Business Age'
        }
        
        readable_name = feature_map.get(feature, feature.replace('_', ' ').title())
        
        sign = "+" if score_impact > 0 else ""
        impact_text = f"{sign}{score_impact} points from {readable_name}"
        
        return impact_text
    
    def _generate_explanation_text(self, contributions: List[Dict]) -> str:
        """
        Generate human-readable explanation
        """
        positive_factors = [c for c in contributions if c['score_impact'] > 0]
        negative_factors = [c for c in contributions if c['score_impact'] < 0]
        
        explanation = []
        
        if positive_factors:
            explanation.append("Positive Factors:")
            for factor in positive_factors[:3]:
                explanation.append(f"  • {factor['impact_text']}")
        
        if negative_factors:
            explanation.append("\nNegative Factors:")
            for factor in negative_factors[:3]:
                explanation.append(f"  • {factor['impact_text']}")
        
        return "\n".join(explanation)
    
    def plot_waterfall(self, X: pd.DataFrame, 
                      feature_names: List[str] = None,
                      max_display: int = 10,
                      save_path: str = None):
        """
        Create SHAP waterfall plot showing feature contributions
        """
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Create waterfall plot
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0],
                base_values=self.explainer.expected_value[1] if isinstance(
                    self.explainer.expected_value, (list, np.ndarray)
                ) else self.explainer.expected_value,
                data=X.iloc[0].values,
                feature_names=feature_names or X.columns.tolist()
            ),
            max_display=max_display
        )
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            print(f"Waterfall plot saved to: {save_path}")
    
    def plot_force(self, X: pd.DataFrame,
                  feature_names: List[str] = None,
                  matplotlib: bool = True,
                  save_path: str = None):
        """
        Create SHAP force plot
        """
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[1]
        
        if matplotlib:
            shap.force_plot(
                base_value,
                shap_values[0],
                X.iloc[0],
                feature_names=feature_names or X.columns.tolist(),
                matplotlib=True,
                show=False
            )
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=150)
                print(f"Force plot saved to: {save_path}")
        else:
            return shap.force_plot(
                base_value,
                shap_values[0],
                X.iloc[0],
                feature_names=feature_names or X.columns.tolist()
            )
    
    def get_summary_plot(self, X: pd.DataFrame,
                        feature_names: List[str] = None,
                        max_display: int = 15,
                        save_path: str = None):
        """
        Create SHAP summary plot for multiple predictions
        """
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        shap.summary_plot(
            shap_values,
            X,
            feature_names=feature_names or X.columns.tolist(),
            max_display=max_display,
            show=False
        )
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            print(f"Summary plot saved to: {save_path}")


if __name__ == "__main__":
    # Example usage
    import sys
    import joblib
    sys.path.append('..')
    
    # Load trained model
    print("Loading model...")
    model_data = joblib.load('../data/credit_risk_xgboost_v1.pkl')
    model = model_data['model']
    feature_names = model_data['feature_names']
    
    # Load test data
    print("Loading test data...")
    test_df = pd.read_csv('../data/test_data.csv')
    
    # Prepare features
    exclude_cols = ['application_id', 'application_date', 'loan_repaid', 
                   'loan_defaulted', 'true_credit_score', 'loan_purpose',
                   'gender', 'marital_status', 'employment_type']
    
    feature_cols = [col for col in test_df.columns if col not in exclude_cols]
    X_test = test_df[feature_cols]
    
    # Initialize explainer
    print("Initializing SHAP explainer...")
    explainer = CreditScoreExplainer(model, X_test[:100])
    
    # Explain a prediction
    print("\n" + "="*60)
    print("SHAP EXPLANATION FOR SAMPLE APPLICATION")
    print("="*60)
    
    sample = X_test.iloc[[0]]
    explanation = explainer.explain_prediction(sample, feature_names=feature_names)
    
    print(f"\nBase Probability: {explanation['base_value']:.4f}")
    print(f"Predicted Probability: {explanation['predicted_probability']:.4f}")
    
    print("\n🎯 Feature Contributions:")
    for contrib in explanation['feature_contributions']:
        print(f"  {contrib['impact_text']}")
    
    print("\n📝 Explanation:")
    print(explanation['explanation_text'])
    
    # Create visualizations
    print("\n📊 Creating SHAP visualizations...")
    explainer.plot_waterfall(sample, feature_names=feature_names, 
                            save_path='../data/shap_waterfall.png')
    
    print("\n✅ SHAP explanation complete!")
