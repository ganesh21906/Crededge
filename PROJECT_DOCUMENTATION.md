# AI Credit Risk Assessment - Project Documentation

## Project Overview
This is a full-stack web application for AI-powered credit risk assessment targeting underserved segments (individuals and SMEs) using alternative data sources.

## Current Project Status: **SKELETON PHASE** ✅

### What's Been Created

#### 1. Frontend (React Application)
- ✅ Complete UI skeleton with 5 pages
- ✅ **Home Page**: Landing page with feature overview
- ✅ **Individual Form**: Comprehensive application form for individuals
- ✅ **SME Form**: Business loan application form
- ✅ **Credit Score Page**: Results display with AI assessment
- ✅ **Dashboard**: Application tracking and statistics
- ✅ **Admin Panel**: Review and approval interface

#### 2. Sample Data Files
- ✅ `sample_applications.json`: Example individual and SME applications
- ✅ `alternative_data_sources.json`: Data source specifications and APIs

#### 3. Backend (FastAPI)
- ✅ Basic REST API structure
- ✅ Mock endpoints for application submission
- ✅ Credit score calculation (mock ML model)
- ✅ CORS configuration for React integration

## Data Points Collected

### Individual Applications
```
PERSONAL INFORMATION:
- Full Name
- Date of Birth
- Gender, Marital Status
- Number of Dependents
- Contact (Mobile, Email)

ADDRESS:
- Full Address
- City, State, Pincode
- Residence Type (Owned/Rented)
- Years at Current Address

EMPLOYMENT:
- Employment Type (Salaried/Self-employed/Freelancer)
- Employer Name
- Monthly Income
- Years Employed
- Industry Type

EDUCATION:
- Highest Qualification

BANKING:
- Bank Account Status
- Bank Name, Account Type
- Average Monthly Balance

ALTERNATIVE DATA:
✓ Utility Bills (6 months)
✓ Rental Agreement & Receipts
✓ UPI/Digital Payment History
✓ Social Media/LinkedIn Profile

LOAN DETAILS:
- Loan Amount Required
- Purpose
- Repayment Period
```

### SME Applications
```
BUSINESS INFORMATION:
- Business Name
- Business Type (Retail/Manufacturing/Services/etc.)
- Registration Type (Proprietorship/Partnership/LLP/Pvt Ltd)
- Year of Establishment
- GST Number
- PAN Number
- Industry Type
- Number of Employees

OWNER INFORMATION:
- Owner/Authorized Person Name
- Designation
- Contact Details

BUSINESS ADDRESS:
- Full Address Details

FINANCIAL INFORMATION:
- Annual Revenue
- Average Monthly Revenue
- Average Monthly Profit
- GST Returns Available
- IT Returns Available

BANKING:
- Bank Account Details
- Average Balance
- Monthly Transaction Count

ALTERNATIVE DATA:
✓ Business Website
✓ Social Media Presence
✓ Utility Bills
✓ Rental Agreement
✓ GST Filing Records

BUSINESS METRICS:
- Customer Base Size
- Number of Suppliers
- Inventory Value
- Business Vintage

LOAN DETAILS:
- Loan Amount
- Purpose (Working Capital/Expansion/Equipment)
- Repayment Period
```

## Alternative Data Sources Used

### 1. **Utility Payment History** (Weight: 25%)
- Electricity bill payments
- Water bill payments
- Mobile bill payments
- Payment regularity percentage
- Delayed payment count

### 2. **Digital Payment Patterns** (Weight: 20%)
- UPI transaction frequency
- Average transaction amounts
- Merchant diversity
- Payment consistency

### 3. **Rental Payments** (Weight: 15%)
- Monthly rent amount
- Payment punctuality
- Tenure at address
- Landlord verification

### 4. **GST & Tax Compliance** (Weight: 30% for SMEs)
- GST filing regularity
- Annual turnover
- Tax payment timeliness

### 5. **Employment Verification** (Weight: 20%)
- Employer details
- Employment duration
- Salary credit patterns
- PF/ESIC verification

### 6. **Educational Background** (Weight: 10%)
- Highest qualification
- Institution tier
- Professional certifications

### 7. **Social Media & Digital Footprint** (Weight: 5%)
- LinkedIn profile completeness
- Professional network size
- Employment verification

### 8. **Bank Transaction Analysis** (Weight: 25%)
- Average account balance
- Deposit regularity
- Spending patterns
- Savings ratio

## Credit Scoring Formula

```
Total Score (0-1000) = Weighted Sum of:

1. Payment History (35%)
   - Utility payment regularity
   - Rent payment consistency
   
2. Income/Revenue Stability (25%)
   - Regular income/revenue patterns
   - Employment/business tenure
   
3. Alternative Data Availability (20%)
   - Number of verified sources
   - Data quality score
   
4. Digital Behavior (15%)
   - UPI transaction patterns
   - Digital payment diversity
   
5. Debt Obligations (5%)
   - Debt-to-income ratio (negative)
```

### Risk Categories
- **Excellent**: 850-1000 (Approval Rate: ~95%)
- **Good**: 750-849 (Approval Rate: ~85%)
- **Fair**: 650-749 (Approval Rate: ~60%)
- **Poor**: Below 650 (Requires Manual Review)

## How to Run the Project

### Frontend Setup
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
# API runs at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

## Next Steps (For Development)

### Phase 1: Core Features
- [ ] Connect frontend to backend APIs
- [ ] Implement actual ML model training
- [ ] Add user authentication (JWT)
- [ ] Database integration (PostgreSQL + MongoDB)

### Phase 2: Alternative Data Integration
- [ ] Integrate BBPS for utility bill verification
- [ ] Connect to GST portal API
- [ ] Implement DigiLocker for document verification
- [ ] Add Aadhaar-based verification (sandbox)

### Phase 3: ML Model Development
- [ ] Collect training dataset
- [ ] Feature engineering pipeline
- [ ] Train XGBoost/LightGBM models
- [ ] Implement SHAP for explainability
- [ ] Model deployment and versioning

### Phase 4: Testing & Deployment
- [ ] Unit testing
- [ ] Integration testing
- [ ] Security audit
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure/GCP)

## API Endpoints (Current)

```
GET  /                          - API info
GET  /health                    - Health check
POST /api/application/individual - Submit individual application
POST /api/application/sme       - Submit SME application
GET  /api/score/{application_id} - Get credit score
GET  /api/applications          - List all applications
GET  /api/stats                 - Dashboard statistics
```

## Technology Stack

**Frontend:**
- React 18
- React Router
- Material-UI / CSS3
- Chart.js
- Axios

**Backend:**
- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn

**Database (To be implemented):**
- PostgreSQL (structured data)
- MongoDB (documents/logs)

**ML Stack (To be implemented):**
- scikit-learn
- XGBoost / LightGBM
- SHAP (explainability)
- Pandas, NumPy
- MLflow (model tracking)

## Sample Data Available

Check `data/` folder for:
- `sample_applications.json` - Example applications
- `alternative_data_sources.json` - Data source specifications

## Notes for Development Team

1. **Sample Data**: All data shown is currently MOCK/SAMPLE data
2. **API Integration**: Real API integration pending (use test/sandbox environments)
3. **Security**: Add proper authentication before production
4. **Privacy**: Ensure GDPR/data privacy compliance
5. **Testing**: Test with various edge cases

## Contact & Team
3rd Semester Mini Project
Industry: BFSI (Banking, Financial Services and Insurance)

---
**Status**: Skeleton Complete ✅ | Ready for Feature Development 🚀
