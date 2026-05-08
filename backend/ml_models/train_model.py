"""
Credit Risk Model Training Script
Trains XGBoost model for credit scoring using alternative data
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, 
                             classification_report)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
from datetime import datetime
import os

class CreditRiskModel:
    """
    XGBoost-based credit risk assessment model
    """
    
    def __init__(self, model_name="credit_risk_xgboost"):
        self.model_name = model_name
        self.model = None
        self.feature_names = None
        self.feature_importance = None
        self.training_history = {}
        
    def train(self, train_df: pd.DataFrame, val_df: pd.DataFrame = None, 
              params: dict = None):
        """
        Train XGBoost model
        """
        print("="*60)
        print("TRAINING CREDIT RISK MODEL")
        print("="*60)
        
        # Prepare data
        X_train, y_train = self._prepare_data(train_df)
        
        if val_df is not None:
            X_val, y_val = self._prepare_data(val_df)
        else:
            X_val, y_val = None, None
        
        # Default XGBoost parameters optimized for credit scoring
        if params is None:
            params = {
                'objective': 'binary:logistic',
                'eval_metric': 'auc',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'min_child_weight': 3,
                'gamma': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                'n_jobs': -1
            }
        
        print(f"\nTraining set: {X_train.shape}")
        print(f"Features: {X_train.shape[1]}")
        print(f"Default rate: {(1 - y_train.mean())*100:.2f}%")
        
        # Train model
        self.model = xgb.XGBClassifier(**params)
        
        if X_val is not None:
            # Train with validation set for early stopping
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_val, y_val)],
                verbose=10
            )
        else:
            self.model.fit(X_train, y_train, verbose=10)
        
        # Store feature names
        self.feature_names = X_train.columns.tolist()
        
        # Calculate feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n✅ Model training complete!")
        
        return self.model
    
    def evaluate(self, test_df: pd.DataFrame, save_plots=True):
        """
        Evaluate model performance
        """
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60)
        
        X_test, y_test = self._prepare_data(test_df)
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'gini': 2 * roc_auc_score(y_test, y_pred_proba) - 1
        }
        
        print(f"\n📊 Performance Metrics:")
        print(f"Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1-Score:  {metrics['f1_score']:.4f}")
        print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"Gini:      {metrics['gini']:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"                  Predicted")
        print(f"                  0 (Default)  1 (Repay)")
        print(f"Actual 0 (Default)  {cm[0,0]:6d}      {cm[0,1]:6d}")
        print(f"Actual 1 (Repay)    {cm[1,0]:6d}      {cm[1,1]:6d}")
        
        # Classification Report
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Default', 'Repay']))
        
        # Save plots
        if save_plots:
            self._plot_evaluation(y_test, y_pred, y_pred_proba, cm)
        
        # Store metrics
        self.training_history['test_metrics'] = metrics
        self.training_history['test_date'] = datetime.now().isoformat()
        
        return metrics
    
    def predict_credit_score(self, application_data: dict) -> dict:
        """
        Predict credit score for a new application
        """
        from feature_engineering import AlternativeDataFeatureEngineering
        
        # Engineer features
        fe = AlternativeDataFeatureEngineering()
        features_dict = fe.engineer_features(application_data)
        
        # Convert to DataFrame
        X = pd.DataFrame([features_dict])
        
        # Ensure all training features are present
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0
        
        # Reorder columns to match training
        X = X[self.feature_names]
        
        # Predict probability
        probability_repaid = self.model.predict_proba(X)[0, 1]
        
        # Convert to credit score (300-900 range, we use 0-1000)
        credit_score = self._probability_to_score(probability_repaid)
        
        # Get risk category
        risk_category, approval_status, interest_rate = self._get_risk_category(credit_score)
        
        # Feature contributions (SHAP-like simplified)
        feature_contributions = self._get_feature_contributions(X)
        
        result = {
            'credit_score': int(credit_score),
            'probability_repaid': float(probability_repaid),
            'risk_category': risk_category,
            'approval_status': approval_status,
            'interest_rate': f"{interest_rate}%",
            'feature_contributions': feature_contributions
        }
        
        return result
    
    def _prepare_data(self, df: pd.DataFrame):
        """
        Prepare features and target from dataframe
        """
        # Target variable
        y = df['loan_repaid']
        
        # Feature columns (exclude ID, date, target columns)
        exclude_cols = ['application_id', 'application_date', 'loan_repaid', 
                       'loan_defaulted', 'true_credit_score', 'loan_purpose',
                       'gender', 'marital_status', 'employment_type']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        X = df[feature_cols]
        
        return X, y
    
    def _probability_to_score(self, probability: float, 
                              min_score: int = 300, 
                              max_score: int = 1000) -> float:
        """
        Convert probability to credit score using log-odds transformation
        """
        # Clamp probability to avoid log(0)
        probability = max(0.01, min(0.99, probability))
        
        # Log-odds transformation
        log_odds = np.log(probability / (1 - probability))
        
        # Scale to score range (center at 650)
        # Log odds range roughly from -5 to +5
        score = 650 + (log_odds * 50)
        
        # Clamp to min/max
        score = max(min_score, min(max_score, score))
        
        return score
    
    def _get_risk_category(self, score: float):
        """
        Determine risk category from credit score
        """
        if score >= 850:
            return "Excellent", "Approved", 10.5
        elif score >= 750:
            return "Good", "Approved", 12.5
        elif score >= 650:
            return "Fair", "Under Review", 15.0
        else:
            return "Poor", "Manual Review Required", 18.0
    
    def _get_feature_contributions(self, X: pd.DataFrame, top_n: int = 10):
        """
        Get top feature contributions (simplified SHAP-like analysis)
        """
        # Get feature importance from model
        importance = self.model.feature_importances_
        
        # Get feature values
        values = X.iloc[0].values
        
        # Calculate contributions (feature_value * importance)
        contributions = []
        for i, (feat, val, imp) in enumerate(zip(self.feature_names, values, importance)):
            contributions.append({
                'feature': feat,
                'value': float(val),
                'importance': float(imp),
                'contribution': float(val * imp)
            })
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)
        
        return contributions[:top_n]
    
    def _plot_evaluation(self, y_test, y_pred, y_pred_proba, cm):
        """
        Create evaluation plots
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Confusion Matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0])
        axes[0, 0].set_title('Confusion Matrix')
        axes[0, 0].set_ylabel('Actual')
        axes[0, 0].set_xlabel('Predicted')
        
        # 2. Feature Importance (Top 15)
        top_features = self.feature_importance.head(15)
        axes[0, 1].barh(range(len(top_features)), top_features['importance'])
        axes[0, 1].set_yticks(range(len(top_features)))
        axes[0, 1].set_yticklabels(top_features['feature'])
        axes[0, 1].set_title('Top 15 Feature Importances')
        axes[0, 1].invert_yaxis()
        
        # 3. Score Distribution
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        axes[1, 0].plot(fpr, tpr, linewidth=2)
        axes[1, 0].plot([0, 1], [0, 1], 'k--')
        axes[1, 0].set_xlabel('False Positive Rate')
        axes[1, 0].set_ylabel('True Positive Rate')
        axes[1, 0].set_title('ROC Curve')
        axes[1, 0].grid(True)
        
        # 4. Prediction Distribution
        axes[1, 1].hist(y_pred_proba[y_test==0], bins=30, alpha=0.5, label='Default')
        axes[1, 1].hist(y_pred_proba[y_test==1], bins=30, alpha=0.5, label='Repay')
        axes[1, 1].set_xlabel('Predicted Probability')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Prediction Distribution by Outcome')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('../data/model_evaluation.png', dpi=150)
        print("\n📊 Evaluation plots saved to: ../data/model_evaluation.png")
        plt.close()
    
    def save_model(self, filepath: str = None):
        """
        Save trained model
        """
        if filepath is None:
            filepath = f'../data/{self.model_name}.pkl'
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'training_history': self.training_history,
            'model_name': self.model_name,
            'saved_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\n💾 Model saved to: {filepath}")
        
        # Save feature importance as JSON
        importance_file = filepath.replace('.pkl', '_features.json')
        self.feature_importance.to_json(importance_file, orient='records', indent=2)
        print(f"💾 Feature importance saved to: {importance_file}")
    
    @classmethod
    def load_model(cls, filepath: str):
        """
        Load trained model
        """
        model_data = joblib.load(filepath)
        
        instance = cls(model_name=model_data['model_name'])
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        instance.feature_importance = model_data['feature_importance']
        instance.training_history = model_data['training_history']
        
        print(f"✅ Model loaded from: {filepath}")
        print(f"   Saved on: {model_data['saved_date']}")
        
        return instance


if __name__ == "__main__":
    # Load generated data
    print("Loading training data...")
    train_df = pd.read_csv('../data/train_data.csv')
    val_df = pd.read_csv('../data/val_data.csv')
    test_df = pd.read_csv('../data/test_data.csv')
    
    print(f"Train: {train_df.shape}")
    print(f"Val:   {val_df.shape}")
    print(f"Test:  {test_df.shape}")
    
    # Initialize and train model
    model = CreditRiskModel(model_name="credit_risk_xgboost_v1")
    
    # Train
    model.train(train_df, val_df)
    
    # Evaluate
    metrics = model.evaluate(test_df, save_plots=True)
    
    # Print top features
    print("\n🎯 Top 10 Most Important Features:")
    print(model.feature_importance.head(10).to_string(index=False))
    
    # Save model
    model.save_model()
    
    print("\n" + "="*60)
    print("✅ MODEL TRAINING COMPLETE!")
    print("="*60)
    print(f"Model: credit_risk_xgboost_v1.pkl")
    print(f"Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Gini Coefficient: {metrics['gini']:.4f}")
