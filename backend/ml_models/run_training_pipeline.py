"""
Complete ML Pipeline Setup Script
1. Generate synthetic training data
2. Train XGBoost model
3. Evaluate performance
4. Save model for API integration
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_data import SyntheticDataGenerator
from train_model import CreditRiskModel
import pandas as pd


def main():
    print("="*70)
    print("CREDIT RISK MODEL - COMPLETE TRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Generate Training Data
    print("\n[STEP 1] Generating synthetic training data...")
    print("-" * 70)
    
    generator = SyntheticDataGenerator(
        n_samples=5000,
        random_state=42
    )
    
    # Generate dataset
    df = generator.generate_dataset()
    
    # Save complete dataset
    generator.save_dataset(df, '../data/complete_dataset.csv')
    
    # Generate train/val/test splits
    train_df, val_df, test_df = generator.generate_train_test_split(df)
    
    print(f"\n✅ Data generation complete!")
    print(f"   Total samples: {len(df)}")
    print(f"   Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"   Val:   {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"   Test:  {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    print(f"   Default rate: {(1-df['loan_repaid'].mean())*100:.2f}%")
    
    # Step 2: Train Model
    print("\n[STEP 2] Training XGBoost model...")
    print("-" * 70)
    
    model = CreditRiskModel(model_name="credit_risk_xgboost_v1")
    
    # Train with custom parameters
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
    
    model.train(train_df, val_df, params=params)
    
    # Step 3: Evaluate Model
    print("\n[STEP 3] Evaluating model performance...")
    print("-" * 70)
    
    metrics = model.evaluate(test_df, save_plots=True)
    
    # Step 4: Save Model
    print("\n[STEP 4] Saving trained model...")
    print("-" * 70)
    
    model.save_model('../data/credit_risk_xgboost_v1.pkl')
    
    # Step 5: Test Prediction
    print("\n[STEP 5] Testing prediction on sample application...")
    print("-" * 70)
    
    # Create a sample application
    sample_application = {
        "personalInfo": {
            "fullName": "Test Applicant",
            "dateOfBirth": "1990-01-01",
            "gender": "Male",
            "maritalStatus": "Single"
        },
        "address": {
            "currentAddress": "123 Test St, Mumbai",
            "yearsAtCurrentAddress": 3
        },
        "employment": {
            "employmentType": "Salaried",
            "employerName": "Tech Corp",
            "monthlyIncome": 50000,
            "yearsAtCurrentJob": 2
        },
        "education": {
            "highestQualification": "Bachelor's Degree"
        },
        "banking": {
            "bankName": "HDFC Bank",
            "accountType": "Savings",
            "averageBalance": 25000
        },
        "alternativeData": {
            "utilityBills": True,
            "rentalAgreement": True,
            "upiTransactions": True,
            "socialMedia": False
        },
        "loanDetails": {
            "loanAmount": 200000,
            "loanPurpose": "Personal",
            "loanTenure": 36
        }
    }
    
    # Make prediction
    result = model.predict_credit_score(sample_application)
    
    print(f"\n📊 Prediction Results:")
    print(f"   Credit Score: {result['credit_score']}")
    print(f"   Risk Category: {result['risk_category']}")
    print(f"   Approval Status: {result['approval_status']}")
    print(f"   Interest Rate: {result['interest_rate']}")
    print(f"   Repayment Probability: {result['probability_repaid']:.2%}")
    
    print(f"\n🎯 Top Feature Contributions:")
    for contrib in result['feature_contributions'][:5]:
        print(f"   {contrib['feature']}: {contrib['contribution']:.4f}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE - MODEL READY FOR DEPLOYMENT")
    print("="*70)
    print(f"\n📁 Saved Files:")
    print(f"   • ../data/complete_dataset.csv - Full dataset")
    print(f"   • ../data/train_data.csv - Training set")
    print(f"   • ../data/val_data.csv - Validation set")
    print(f"   • ../data/test_data.csv - Test set")
    print(f"   • ../data/credit_risk_xgboost_v1.pkl - Trained model")
    print(f"   • ../data/credit_risk_xgboost_v1_features.json - Feature importance")
    print(f"   • ../data/model_evaluation.png - Evaluation plots")
    
    print(f"\n📊 Model Performance:")
    print(f"   • Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"   • Precision: {metrics['precision']*100:.2f}%")
    print(f"   • Recall:    {metrics['recall']*100:.2f}%")
    print(f"   • F1-Score:  {metrics['f1_score']*100:.2f}%")
    print(f"   • ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"   • Gini:      {metrics['gini']:.4f}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review model performance metrics")
    print(f"   2. Update backend API to use trained model")
    print(f"   3. Test API endpoints with real predictions")
    print(f"   4. Deploy to production")
    
    return model, metrics


if __name__ == "__main__":
    model, metrics = main()
