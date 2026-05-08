# Data Flow & Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (React)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Home     │  │ Individual │  │    SME     │            │
│  │   Page     │  │    Form    │  │   Form     │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Credit    │  │ Dashboard  │  │   Admin    │            │
│  │   Score    │  │            │  │   Panel    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  POST /api/application/individual                      │ │
│  │  POST /api/application/sme                            │ │
│  │  GET  /api/score/{id}                                 │ │
│  │  GET  /api/applications                               │ │
│  │  GET  /api/stats                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↕                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           CREDIT SCORING ENGINE (ML Model)             │ │
│  │  - Feature Engineering                                 │ │
│  │  - XGBoost/LightGBM Model                             │ │
│  │  - Risk Classification                                │ │
│  │  - Explainability (SHAP)                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                        │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │   PostgreSQL     │        │     MongoDB      │          │
│  │  (Structured)    │        │  (Unstructured)  │          │
│  │  - User Data     │        │  - Documents     │          │
│  │  - Applications  │        │  - Logs          │          │
│  │  - Scores        │        │  - Audit Trail   │          │
│  └──────────────────┘        └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL DATA SOURCES (APIs)                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │  BBPS   │ │   GST   │ │DigiLockr│ │  UPI    │          │
│  │Utility  │ │ Portal  │ │  Docs   │ │ Data    │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Individual Application

```
STEP 1: User Fills Form
┌────────────────────────────────────────────────┐
│  Individual Application Form                   │
│  ✓ Personal Info (Name, DOB, Contact)         │
│  ✓ Address Details                             │
│  ✓ Employment Info (Salary, Employer)          │
│  ✓ Education                                   │
│  ✓ Banking Details                             │
│  ✓ Alternative Data (Checkboxes)               │
│  ✓ Loan Details (Amount, Purpose)              │
└────────────────────────────────────────────────┘
                    ↓
STEP 2: Frontend Validation
┌────────────────────────────────────────────────┐
│  Client-side Validation                        │
│  ✓ Required fields check                       │
│  ✓ Format validation (phone, email, PAN)       │
│  ✓ Numeric range checks                        │
└────────────────────────────────────────────────┘
                    ↓
STEP 3: API Call (POST)
┌────────────────────────────────────────────────┐
│  POST /api/application/individual              │
│  Headers: Content-Type: application/json       │
│  Body: {                                       │
│    fullName: "Rajesh Kumar",                   │
│    monthlyIncome: 50000,                       │
│    loanAmount: 200000,                         │
│    hasUtilityBills: true,                      │
│    ...                                         │
│  }                                             │
└────────────────────────────────────────────────┘
                    ↓
STEP 4: Backend Processing
┌────────────────────────────────────────────────┐
│  FastAPI Backend Receives Data                 │
│  1. Validate using Pydantic models             │
│  2. Generate Application ID (IND-XXXXX)        │
│  3. Extract features for ML model              │
└────────────────────────────────────────────────┘
                    ↓
STEP 5: Feature Engineering
┌────────────────────────────────────────────────┐
│  Calculate ML Features:                        │
│  • payment_regularity_score = 95              │
│  • income_stability_index = 0.85              │
│  • digital_footprint_score = 88               │
│  • employment_tenure_months = 36              │
│  • debt_to_income_ratio = 0.3                 │
│  • alternative_data_count = 4                 │
└────────────────────────────────────────────────┘
                    ↓
STEP 6: ML Model Prediction
┌────────────────────────────────────────────────┐
│  Credit Scoring Model (XGBoost)                │
│  Input: [95, 0.85, 88, 36, 0.3, 4, ...]       │
│                  ↓                             │
│  Model Output: Credit Score = 782              │
│                  ↓                             │
│  Risk Category: Good (750-849)                 │
└────────────────────────────────────────────────┘
                    ↓
STEP 7: Explainability Analysis
┌────────────────────────────────────────────────┐
│  SHAP Analysis - Factor Contributions:         │
│  • Payment History: +120 points (35%)          │
│  • Income Stability: +98 points (25%)          │
│  • Alternative Data: +78 points (20%)          │
│  • Employment: +58 points (15%)                │
│  • Debt Burden: +25 points (5%)                │
└────────────────────────────────────────────────┘
                    ↓
STEP 8: Generate Response
┌────────────────────────────────────────────────┐
│  API Response:                                 │
│  {                                             │
│    applicationId: "IND-12345",                 │
│    creditScore: 782,                           │
│    riskCategory: "Good",                       │
│    approvalStatus: "Approved",                 │
│    interestRate: "12.5%",                      │
│    maxLoanEligible: "₹3,50,000",              │
│    factors: [...],                             │
│    strengths: [...],                           │
│    improvements: [...],                        │
│    recommendations: [...]                      │
│  }                                             │
└────────────────────────────────────────────────┘
                    ↓
STEP 9: Display Results
┌────────────────────────────────────────────────┐
│  Credit Score Page                             │
│  🎯 Score: 782/1000                            │
│  📊 Risk: Good                                 │
│  ✅ Status: Approved                           │
│  💰 Max Eligible: ₹3,50,000                    │
│  📈 Factor Breakdown                           │
│  💪 Strengths List                             │
│  ⚠️  Areas for Improvement                     │
└────────────────────────────────────────────────┘
```

## Alternative Data Collection Flow

```
┌─────────────────────────────────────────────────┐
│         ALTERNATIVE DATA SOURCES                │
└─────────────────────────────────────────────────┘

1. UTILITY BILLS (Weight: 25%)
   User Upload → Document Verification → Extract Data
   ├─ Bill Amount: ₹2,500/month
   ├─ Payment Date: On-time for 6 months
   ├─ Regularity Score: 95%
   └─ Contribution: +120 points to credit score

2. UPI TRANSACTION HISTORY (Weight: 20%)
   User Consent → API Integration → Transaction Analysis
   ├─ Transaction Count: 142/month
   ├─ Merchant Diversity: 42 unique merchants
   ├─ Avg Amount: ₹1,200
   └─ Contribution: +95 points to credit score

3. RENTAL AGREEMENT (Weight: 15%)
   Upload Agreement → Landlord Verification → Payment History
   ├─ Monthly Rent: ₹15,000
   ├─ Tenure: 36 months
   ├─ Payment Punctuality: 92%
   └─ Contribution: +70 points to credit score

4. GST RETURNS (For SMEs - Weight: 30%)
   GST Number → Portal API → Filing Analysis
   ├─ Filing Regularity: 100%
   ├─ Annual Turnover: ₹50L
   ├─ Tax Payment: On-time
   └─ Contribution: +180 points to credit score

5. EMPLOYMENT VERIFICATION (Weight: 20%)
   LinkedIn Profile → EPFO Data → Salary Slips
   ├─ Employer: Verified
   ├─ Tenure: 48 months
   ├─ Salary Credit: Regular
   └─ Contribution: +95 points to credit score

TOTAL CREDIT SCORE = Sum of all weighted factors
```

## Admin Review Workflow

```
Application Submitted
        ↓
   AI Analysis
        ↓
┌───────────────────┐
│ Credit Score: 782 │
│ Risk: Good        │
│ AI Confidence: 87%│
└───────────────────┘
        ↓
┌─────────────────────────────────────┐
│  If Score >= 850:                   │
│    → Auto-Approve                   │
│  If Score 750-849:                  │
│    → Auto-Approve with conditions   │
│  If Score 650-749:                  │
│    → Manual Review Required         │
│  If Score < 650:                    │
│    → Detailed Manual Review         │
└─────────────────────────────────────┘
        ↓
Admin Dashboard
        ↓
┌────────────────────────────┐
│  Admin Actions:            │
│  ✓ View AI Recommendation  │
│  ✓ Review Documents        │
│  ✓ Check Factor Breakdown  │
│  ✓ Approve / Reject        │
│  ✓ Request More Info       │
└────────────────────────────┘
        ↓
  Final Decision
        ↓
   User Notification
```

## What Sample Data Shows

### In Forms:
- **Placeholders**: Show expected format (e.g., "9876543210" for phone)
- **Dropdown Options**: Display available choices
- **Checkbox Labels**: Indicate what documents can be provided
- **Help Text**: Explain what each field means

### In Responses:
- **Credit Score**: Numerical value (650-1000)
- **Risk Category**: Text label (Excellent/Good/Fair/Poor)
- **Factor Breakdown**: Shows contribution of each data source
- **Recommendations**: AI-generated suggestions
- **Approval Status**: Current application state

### In Dashboard:
- **Statistics Cards**: Total applications, approved, pending, rejected
- **Recent Applications Table**: List of submitted applications
- **Charts**: Distribution by type, risk category
- **Metrics**: Average score, approval rate, processing time

---
**This diagram shows how data flows from user input through AI analysis to final decision**
