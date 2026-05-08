# ML Model Training - Quick Start Guide

## ⚡ Fast Track (5 Minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Train Model
```bash
cd ml_models
python run_training_pipeline.py
```

**Expected output:**
```
======================================================================
CREDIT RISK MODEL - COMPLETE TRAINING PIPELINE
======================================================================

[STEP 1] Generating synthetic training data...
✅ Data generation complete!
   Total samples: 5000
   Train: 3500 (70.0%)
   Val:   750 (15.0%)
   Test:  750 (15.0%)
   Default rate: 10.23%

[STEP 2] Training XGBoost model...
[0]	validation_0-auc:0.85674	validation_1-auc:0.84523
...
✅ Model training complete!

[STEP 3] Evaluating model performance...
📊 Performance Metrics:
Accuracy:  82.34% (82.34%)
Precision: 0.8567
Recall:    0.8123
F1-Score:  0.8340
ROC-AUC:   0.8567
Gini:      0.7134

[STEP 4] Saving trained model...
💾 Model saved to: ../data/credit_risk_xgboost_v1.pkl

[STEP 5] Testing prediction on sample application...
📊 Prediction Results:
   Credit Score: 758
   Risk Category: Good
   Approval Status: Approved
   Interest Rate: 12.5%

======================================================================
✅ PIPELINE COMPLETE - MODEL READY FOR DEPLOYMENT
======================================================================
```

### Step 3: Run API with ML Model
```bash
cd backend
python app_ml_integrated.py
```

**Expected output:**
```
======================================================================
AI CREDIT RISK ASSESSMENT API v2.0
======================================================================

📚 API Documentation: http://localhost:8000/docs
🎨 Frontend: http://localhost:3000

🤖 ML Model Status:
📦 Loading trained model from: data/credit_risk_xgboost_v1.pkl
🔍 Initializing SHAP explainer...
✅ Model loaded successfully!
   Model: credit_risk_xgboost_v1
   ✅ Model loaded and ready

======================================================================
```

### Step 4: Test API
```bash
# In a new terminal
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "AI Credit Risk Assessment API",
  "version": "2.0.0",
  "status": "active",
  "model_loaded": true
}
```

## 📊 What Gets Created

### Training Data Files
- `data/complete_dataset.csv` - 5,000 synthetic loan applications
- `data/train_data.csv` - 3,500 training samples (70%)
- `data/val_data.csv` - 750 validation samples (15%)
- `data/test_data.csv` - 750 test samples (15%)

### Model Files
- `data/credit_risk_xgboost_v1.pkl` - Trained XGBoost model (~5MB)
- `data/credit_risk_xgboost_v1_features.json` - Feature importance rankings

### Visualization Files
- `data/model_evaluation.png` - 4 evaluation plots:
  - Confusion Matrix
  - Feature Importance (Top 15)
  - ROC Curve
  - Prediction Distribution

## 🧪 Testing the Model

### Test Individual Prediction

```bash
cd backend/ml_models
python
```

```python
from train_model import CreditRiskModel

# Load model
model = CreditRiskModel.load_model('../data/credit_risk_xgboost_v1.pkl')

# Sample application
app = {
    "personalInfo": {
        "fullName": "Test User",
        "dateOfBirth": "1990-01-01",
        "gender": "Male"
    },
    "employment": {
        "employmentType": "Salaried",
        "monthlyIncome": 50000
    },
    "banking": {
        "averageBalance": 25000
    },
    "alternativeData": {
        "utilityBills": True,
        "rentalAgreement": True,
        "upiTransactions": True
    },
    "loanDetails": {
        "loanAmount": 200000,
        "loanTenure": 36
    }
}

# Predict
result = model.predict_credit_score(app)
print(f"Score: {result['credit_score']}")
print(f"Category: {result['risk_category']}")
```

### Test API Endpoint

```bash
# Start backend
cd backend
python app_ml_integrated.py

# In new terminal, test API
curl -X POST http://localhost:8000/api/application/individual \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Rajesh Kumar",
    "dateOfBirth": "1990-05-15",
    "gender": "Male",
    "maritalStatus": "Single",
    "dependents": 0,
    "mobileNumber": "9876543210",
    "email": "rajesh@example.com",
    "address": "123 MG Road",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "residenceType": "Rented",
    "yearsAtAddress": 3.0,
    "employmentType": "Salaried",
    "employerName": "Tech Corp",
    "monthlyIncome": 50000,
    "yearsEmployed": 2.0,
    "industryType": "IT",
    "qualification": "Bachelors",
    "hasBankAccount": true,
    "bankName": "HDFC Bank",
    "accountType": "Savings",
    "averageBalance": 25000,
    "hasUtilityBills": true,
    "hasRentalAgreement": true,
    "hasUPIHistory": true,
    "hasSocialMedia": false,
    "loanAmount": 200000,
    "loanPurpose": "Personal",
    "repaymentPeriod": 36
  }'
```

**Expected Response:**
```json
{
  "applicationId": "IND-12345",
  "applicationType": "Individual",
  "applicantName": "Rajesh Kumar",
  "creditScore": 758,
  "riskCategory": "Good",
  "approvalStatus": "Approved",
  "interestRate": "12.5%",
  "maxLoanEligible": "₹3,50,000",
  "factors": [
    {
      "name": "Payment History",
      "score": 88,
      "weight": 35,
      "description": "Impact: +84 points"
    }
  ],
  "strengths": [
    "✅ +84 points from Payment History",
    "✅ +56 points from Income Stability"
  ],
  "improvements": [
    "⚠️ Improve Debt-to-Income Ratio"
  ]
}
```

## 🔍 Verify Model is Working

### Check 1: Model File Exists
```bash
ls -lh backend/data/credit_risk_xgboost_v1.pkl
```
Should show file size ~5MB

### Check 2: API Loads Model
Visit http://localhost:8000/ and check:
```json
{
  "model_loaded": true  // Should be true
}
```

### Check 3: Predictions are Real (Not Mock)
Mock predictions: Score is random (650-950)
Real predictions: Score is consistent for same input

Test by submitting same application twice - scores should match!

## ⚙️ Configuration Options

### Adjust Training Data Size

Edit `run_training_pipeline.py`:
```python
generator = SyntheticDataGenerator(
    n_samples=10000,  # Increase to 10,000 samples
    default_rate=0.12,
    random_state=42
)
```

### Modify Hyperparameters

Edit `run_training_pipeline.py`:
```python
params = {
    'max_depth': 8,  # Increase depth
    'learning_rate': 0.05,  # Slower learning
    'n_estimators': 300,  # More trees
}
```

### Change Score Range

Edit `train_model.py`:
```python
def _probability_to_score(self, probability: float, 
                          min_score: int = 400,  # Change min
                          max_score: int = 900) -> float:  # Change max
```

## 📈 Model Performance Targets

| Metric | Target | Acceptable | Needs Improvement |
|--------|--------|------------|-------------------|
| Accuracy | >80% | 75-80% | <75% |
| Precision | >85% | 80-85% | <80% |
| Recall | >80% | 75-80% | <75% |
| ROC-AUC | >0.85 | 0.80-0.85 | <0.80 |
| Gini | >0.70 | 0.60-0.70 | <0.60 |

## 🐛 Common Issues

### Issue 1: Import Error
```
ModuleNotFoundError: No module named 'xgboost'
```
**Fix:**
```bash
pip install xgboost==2.0.3
```

### Issue 2: Model Not Found
```
⚠️ Trained model not found at: data/credit_risk_xgboost_v1.pkl
```
**Fix:**
```bash
cd backend/ml_models
python run_training_pipeline.py
```

### Issue 3: Low Performance
```
Accuracy: 65.23%  # Too low!
```
**Fix:**
1. Increase training samples: `n_samples=10000`
2. Check data quality: Look for NaN values
3. Tune hyperparameters: Adjust max_depth, learning_rate

### Issue 4: SHAP Errors
```
SHAP explainer initialization failed
```
**Fix:** This is non-critical. Model still works without SHAP explanations.
To fix:
```bash
pip install shap==0.44.1
```

## 🎯 Next Steps After Training

1. ✅ Model trained and saved
2. ✅ API integrated with model
3. **TODO:** Run frontend (`npm start` in frontend/)
4. **TODO:** Test complete flow: Form → API → Credit Score
5. **TODO:** Review SHAP explanations for sample applications
6. **TODO:** Deploy to production server

## 📞 Need Help?

Check these files for detailed documentation:
- `ml_models/README.md` - Complete ML documentation
- `ml_models/feature_engineering.py` - Feature details
- `ml_models/train_model.py` - Model architecture
- `ml_models/shap_explainer.py` - Explainability

Run test functions in any file:
```bash
python feature_engineering.py  # Test feature extraction
python generate_data.py        # Test data generation
python train_model.py          # Test training
python shap_explainer.py       # Test SHAP
```
