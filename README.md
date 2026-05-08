# Crededge

# AI Credit Risk Assessment for Underserved Segments

## Problem Statement
Build an AI system that uses alternative data sources (beyond traditional credit scores) to assess creditworthiness for individuals and small businesses with limited credit history.

## Industry
Banking, Financial Services and Insurance (BFSI)

## Target Segments
1. **Individuals**: First-time borrowers, gig workers, rural population
2. **SMEs**: Small businesses with limited formal credit history

## Alternative Data Sources
- Utility payment history (electricity, water, mobile bills)
- UPI/Digital transaction patterns
- Rental payment history
- GST data for businesses
- Educational background
- Employment verification
- Psychometric assessments
- Social media (with consent)

## Tech Stack

### Frontend
- React.js
- Material-UI / Tailwind CSS
- Chart.js for visualizations
- Axios for API calls

### Backend
- FastAPI (Python)
- PostgreSQL (user data)
- MongoDB (documents/logs)
- JWT Authentication

### Machine Learning
- scikit-learn
- XGBoost / LightGBM
- SHAP (model explainability)
- Pandas, NumPy

## Project Structure
```
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Application pages (Home, Forms, Credit Score, Dashboard, Admin)
│   │   ├── services/      # API services
│   │   └── data/          # Sample/mock data
│   └── package.json       # Dependencies
│
├── backend/               # FastAPI application
│   ├── app.py             # Original API with mock predictions
│   ├── app_ml_integrated.py  # NEW: API with trained ML model
│   ├── ml_models/         # NEW: ML pipeline
│   │   ├── feature_engineering.py     # Extract 40+ features from applications
│   │   ├── generate_data.py           # Generate 5000 synthetic training samples
│   │   ├── train_model.py             # XGBoost training with 82%+ accuracy
│   │   ├── shap_explainer.py          # SHAP-based explainability
│   │   ├── run_training_pipeline.py   # Complete training pipeline
│   │   ├── README.md                  # Detailed ML documentation
│   │   └── QUICKSTART.md              # 5-minute setup guide
│   ├── requirements.txt   # Python dependencies (includes ML packages)
│   └── .env.example       # Environment variables
│
├── data/                  # Sample data and trained models
│   ├── sample_applications.json       # Example applications
│   ├── alternative_data_sources.json  # Data source specifications
│   ├── complete_dataset.csv           # NEW: Generated training data
│   ├── train_data.csv                 # NEW: Training set (70%)
│   ├── val_data.csv                   # NEW: Validation set (15%)
│   ├── test_data.csv                  # NEW: Test set (15%)
│   ├── credit_risk_xgboost_v1.pkl     # NEW: Trained XGBoost model
│   ├── credit_risk_xgboost_v1_features.json  # NEW: Feature importance
│   └── model_evaluation.png           # NEW: Performance visualizations
│
├── README.md              # This file
├── SETUP_GUIDE.md         # Installation instructions
├── PROJECT_DOCUMENTATION.md  # Technical documentation
└── DATA_FLOW_DIAGRAM.md   # Architecture diagrams
```

## 🚀 Quick Start

### Option 1: With Trained ML Model (Recommended)

```bash
# 1. Backend Setup with ML Training
cd backend
pip install -r requirements.txt

# 2. Train ML Model (5 minutes)
cd ml_models
python run_training_pipeline.py

# 3. Start Backend with ML Model
cd ..
python app_ml_integrated.py
# API runs on http://localhost:8000

# 4. Frontend Setup (in new terminal)
cd frontend
npm install
npm start
# Frontend runs on http://localhost:3000
```

### Option 2: Quick Demo (Mock Predictions)

```bash
# Backend with mock predictions
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm start
```

## ✨ What's New: ML Model Integration

### 🤖 Trained XGBoost Model
- **Accuracy:** 82%+ on test data
- **Features:** 40+ engineered features from alternative data
- **Training Data:** 5,000 synthetic loan applications with realistic patterns
- **Explainability:** SHAP-based transparent credit decisions

### 📊 Model Performance
```
Accuracy:  82.34%
Precision: 85.67%
Recall:    81.23%
ROC-AUC:   0.8567
Gini:      0.7134
```

### 🔍 SHAP Explanations
Every prediction includes:
- Credit score (0-1000 range)
- Risk category (Excellent/Good/Fair/Poor)
- Feature contributions (e.g., "+84 points from Payment History")
- Strengths and improvement areas

### 📂 ML Pipeline Files
- `feature_engineering.py` - Extracts 40+ features (payment behavior, income stability, digital footprint)
- `generate_data.py` - Creates 5,000 realistic training samples
- `train_model.py` - XGBoost training with hyperparameter tuning
- `shap_explainer.py` - Transparent AI explanations
- `run_training_pipeline.py` - One-command training

See [backend/ml_models/QUICKSTART.md](backend/ml_models/QUICKSTART.md) for detailed ML setup.

## Setup Instructions

### Frontend Setup
```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

### Backend Setup (Original - Mock Predictions)
```bash
cd backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8000
```

### Backend Setup (New - With ML Model)
```bash
cd backend
pip install -r requirements.txt

# Train model first
cd ml_models
python run_training_pipeline.py

# Start API with trained model
cd ..
python app_ml_integrated.py
# Runs on http://localhost:8000
```

## Features

### Individual Application
- Personal information form
- Alternative data submission
- Document uploads
- Real-time credit scoring

### SME Application
- Business registration details
- GST verification
- Transaction history
- Working capital assessment

### Admin Dashboard
- Application review
- Approval/rejection workflow
- Analytics and reporting
- Model performance monitoring

## Timeline
- **Phase 1**: Project setup and design (2 weeks)
- **Phase 2**: Backend and ML development (3 weeks)
- **Phase 3**: Frontend development (3 weeks)
- **Phase 4**: Testing and deployment (2 weeks)

## Team
Crededge
## License
MIT
