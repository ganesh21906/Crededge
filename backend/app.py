"""
Crededge API v2.0 - Consolidated Backend
AI Credit Risk Assessment for Underserved Segments

Single entry point. Supports:
- Rule-based scoring (default, works without training)
- ML model scoring (set USE_ML_MODEL=true in .env)
- SQLite persistence (no external DB required)
- JWT auth for admin endpoints
- UUID-based application IDs
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta
import uuid
import os
import json

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("JWT_SECRET", "crededge-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crededge.db")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

USE_ML_MODEL = os.getenv("USE_ML_MODEL", "false").lower() == "true"

# Score thresholds (single source of truth)
THRESHOLD_EXCELLENT = 850
THRESHOLD_GOOD = 750
THRESHOLD_FAIR = 650

SCORE_CONFIG = {
    "Excellent": {
        "min": THRESHOLD_EXCELLENT, "status": "Approved",
        "rate": "10.5%", "individual_max": 500000, "sme_max": 2500000
    },
    "Good": {
        "min": THRESHOLD_GOOD, "status": "Approved",
        "rate": "12.5%", "individual_max": 350000, "sme_max": 1800000
    },
    "Fair": {
        "min": THRESHOLD_FAIR, "status": "Under Review",
        "rate": "15.0%", "individual_max": 200000, "sme_max": 1200000
    },
    "Poor": {
        "min": 0, "status": "Requires Additional Review",
        "rate": "18.0%", "individual_max": 100000, "sme_max": 800000
    },
}

# ============================================================
# DATABASE SETUP (SQLite - zero configuration required)
# ============================================================

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ApplicationDB(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, index=True)
    application_type = Column(String)          # "Individual" | "SME"
    applicant_name = Column(String, index=True)
    email = Column(String)
    phone = Column(String)
    loan_amount = Column(Float)
    loan_purpose = Column(String)
    credit_score = Column(Integer)
    risk_category = Column(String)
    approval_status = Column(String)
    interest_rate = Column(String)
    max_loan_eligible = Column(String)
    review_status = Column(String, default="pending")  # pending | approved | rejected
    ai_confidence = Column(Float)
    model_used = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)
    full_data_json = Column(Text)    # Serialized full application payload
    factors_json = Column(Text)      # Score factor breakdown
    strengths_json = Column(Text)
    improvements_json = Column(Text)
    recommendations_json = Column(Text)
    coach_tips_json = Column(Text)   # AI Financial Coach tips


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# JWT AUTH
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# ============================================================
# ML MODEL LOADING (optional)
# ============================================================

ml_model = None
if USE_ML_MODEL:
    try:
        import joblib
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ml_models"))
        model_path = os.path.join(os.path.dirname(__file__), "../data/credit_risk_xgboost_v1.pkl")
        ml_model = joblib.load(model_path)
        print("✅ XGBoost ML model loaded successfully")
    except Exception as e:
        print(f"⚠️  ML model not found — falling back to rule-based engine: {e}")
        USE_ML_MODEL = False

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Crededge API",
    description="AI Credit Risk Assessment for Underserved Segments — BFSI Mini Project",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ============================================================
# PYDANTIC MODELS
# ============================================================

class IndividualApplication(BaseModel):
    fullName: str
    dateOfBirth: Optional[str] = None
    gender: str
    maritalStatus: str
    dependents: int
    mobileNumber: str
    email: str
    address: str
    city: str
    state: str
    pincode: str
    residenceType: str
    yearsAtAddress: float
    employmentType: str
    employerName: Optional[str] = None
    monthlyIncome: float
    yearsEmployed: Optional[float] = None
    industryType: Optional[str] = None
    qualification: str
    hasBankAccount: Optional[bool] = False
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    hasUtilityBills: Optional[bool] = False
    hasRentalAgreement: Optional[bool] = False
    hasUPIHistory: Optional[bool] = False
    hasSocialMedia: Optional[bool] = False
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int


class SMEApplication(BaseModel):
    businessName: str
    businessType: str
    registrationType: str
    yearOfEstablishment: int
    gstNumber: Optional[str] = None
    panNumber: str
    industryType: str
    numberOfEmployees: str
    ownerName: str
    designation: str
    mobileNumber: str
    email: str
    address: str
    city: str
    state: str
    pincode: str
    annualRevenue: float
    monthlyRevenue: float
    averageMonthlyProfit: float
    hasGSTReturns: Optional[bool] = False
    hasITReturns: Optional[bool] = False
    hasBankAccount: Optional[bool] = False
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    monthlyTransactions: Optional[int] = None
    hasBusinessWebsite: Optional[bool] = False
    websiteUrl: Optional[str] = None
    hasDigitalPresence: Optional[bool] = False
    socialMediaLinks: Optional[str] = None
    hasUtilityBills: Optional[bool] = False
    hasRentalAgreement: Optional[bool] = False
    customerBase: Optional[str] = None
    supplierCount: Optional[str] = None
    hasInventory: Optional[bool] = False
    inventoryValue: Optional[float] = None
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int


class AdminActionRequest(BaseModel):
    action: str  # "approved" | "rejected"
    note: Optional[str] = None

# ============================================================
# CREDIT SCORING ENGINE
# ============================================================

def _get_category(score: int) -> str:
    if score >= THRESHOLD_EXCELLENT:
        return "Excellent"
    elif score >= THRESHOLD_GOOD:
        return "Good"
    elif score >= THRESHOLD_FAIR:
        return "Fair"
    return "Poor"


def _generate_coach_tips(factors: list, app_data: dict, app_type: str) -> list:
    """AI Financial Coach — rule-based personalized improvement tips."""
    tips = []
    factor_map = {f["name"]: f["score"] for f in factors}

    if factor_map.get("Payment History", 100) < 80:
        tips.append({
            "icon": "💡",
            "title": "Pay Bills Consistently",
            "tip": "Paying electricity, water, and mobile bills on time every month can add +40 to +60 points within 6 months.",
            "impact": "High",
            "timeframe": "6 months"
        })

    if factor_map.get("Alternative Data", 100) < 80:
        tips.append({
            "icon": "📱",
            "title": "Activate UPI Payments",
            "tip": "Regular UPI transactions (10+ per month) demonstrate financial activity and can boost your score by +30 to +50 points.",
            "impact": "High",
            "timeframe": "3 months"
        })

    if factor_map.get("Income Stability", 100) < 75:
        tips.append({
            "icon": "💰",
            "title": "Stabilize Your Income",
            "tip": "Consistent income credited to the same bank account for 3+ consecutive months significantly improves income stability score.",
            "impact": "Very High",
            "timeframe": "3-6 months"
        })

    if not app_data.get("hasBankAccount") and not app_data.get("hasBankAccount"):
        tips.append({
            "icon": "🏦",
            "title": "Open a Bank Account",
            "tip": "A formal bank account is the foundation of credit history. Open one today and maintain a minimum balance of ₹5,000.",
            "impact": "Very High",
            "timeframe": "Immediate"
        })

    if app_type == "Individual" and not app_data.get("hasRentalAgreement"):
        tips.append({
            "icon": "🏠",
            "title": "Register Your Rental Agreement",
            "tip": "A registered rental agreement proves address stability. This can add +20 to your profile score.",
            "impact": "Medium",
            "timeframe": "1 month"
        })

    if app_type == "SME":
        if not app_data.get("hasGSTReturns"):
            tips.append({
                "icon": "📊",
                "title": "File GST Returns Regularly",
                "tip": "Filing GST returns monthly/quarterly is a major trust signal for SME lending. It can add +50 to +80 points.",
                "impact": "Very High",
                "timeframe": "3 months"
            })
        if not app_data.get("hasBusinessWebsite"):
            tips.append({
                "icon": "🌐",
                "title": "Create a Business Website",
                "tip": "A simple business website adds legitimacy and digital presence, contributing +10 to +15 points.",
                "impact": "Low",
                "timeframe": "2 weeks"
            })

    # Generic tip always shown
    tips.append({
        "icon": "📈",
        "title": "Build Data History Over Time",
        "tip": "Consistently providing more data points each month builds a stronger credit profile. Track your score every 3 months.",
        "impact": "Medium",
        "timeframe": "Ongoing"
    })

    return tips[:5]  # Return top 5 most relevant tips


def rule_based_score(app_data: dict, app_type: str) -> dict:
    """
    Deterministic rule-based credit scoring.
    Uses actual submitted data — NO random values.
    """
    score = 500  # Base score

    # --- Payment History (35% weight) ---
    payment_score = 60
    if app_data.get("hasUtilityBills"):
        score += 50
        payment_score += 15
    if app_data.get("hasUPIHistory"):
        score += 40
        payment_score += 12
    if app_data.get("hasRentalAgreement"):
        score += 25
        payment_score += 8
    payment_score = min(payment_score, 95)

    # --- Income Stability (25% weight) ---
    income_score = 60
    if app_type == "Individual":
        income = app_data.get("monthlyIncome", 0) or 0
        if income >= 75000:
            score += 80
            income_score += 25
        elif income >= 50000:
            score += 60
            income_score += 18
        elif income >= 30000:
            score += 35
            income_score += 10
        elif income >= 15000:
            score += 15
            income_score += 5

        emp = (app_data.get("employmentType") or "").lower()
        if emp == "salaried":
            score += 45
            income_score += 10
        elif emp in ["self-employed", "business"]:
            score += 25
            income_score += 6
        elif emp == "freelancer":
            score += 10
            income_score += 3

        years_emp = app_data.get("yearsEmployed") or 0
        if years_emp >= 5:
            score += 30
            income_score += 8
        elif years_emp >= 2:
            score += 15
            income_score += 4

        qual = (app_data.get("qualification") or "").lower()
        if qual in ["postgraduate", "professional"]:
            score += 20
        elif qual == "graduate":
            score += 12
        elif qual == "diploma":
            score += 6

    else:  # SME
        revenue = app_data.get("annualRevenue", 0) or 0
        if revenue >= 5000000:
            score += 80
            income_score += 25
        elif revenue >= 2000000:
            score += 55
            income_score += 18
        elif revenue >= 500000:
            score += 30
            income_score += 10
        elif revenue >= 100000:
            score += 10
            income_score += 4

        profit = app_data.get("averageMonthlyProfit", 0) or 0
        if profit > 0:
            profit_margin = profit / max(app_data.get("monthlyRevenue", 1), 1)
            if profit_margin >= 0.2:
                score += 25
                income_score += 8
            elif profit_margin >= 0.1:
                score += 12
                income_score += 4

        if app_data.get("hasGSTReturns"):
            score += 50
            income_score += 10
        if app_data.get("hasITReturns"):
            score += 25
            income_score += 5

        vintage = datetime.now().year - (app_data.get("yearOfEstablishment") or datetime.now().year)
        if vintage >= 5:
            score += 40
            income_score += 10
        elif vintage >= 2:
            score += 20
            income_score += 5

    income_score = min(income_score, 95)

    # --- Alternative Data (20% weight) ---
    alt_score = 65
    if app_data.get("hasBankAccount"):
        score += 20
        alt_score += 10
        bal = app_data.get("averageBalance") or 0
        if bal >= 100000:
            score += 30
            alt_score += 12
        elif bal >= 30000:
            score += 15
            alt_score += 6
    if app_data.get("hasSocialMedia") or app_data.get("hasDigitalPresence"):
        score += 15
        alt_score += 5
    if app_type == "SME" and app_data.get("hasBusinessWebsite"):
        score += 15
        alt_score += 5
    if app_type == "SME" and (app_data.get("monthlyTransactions") or 0) > 100:
        score += 20
        alt_score += 8
    alt_score = min(alt_score, 95)

    # --- Employment/Business Profile (15% weight) ---
    emp_biz_score = 70
    if app_type == "SME":
        reg = (app_data.get("registrationType") or "").lower()
        if reg in ["private-limited", "public-limited", "llp"]:
            score += 20
            emp_biz_score += 10
        elif reg == "partnership":
            score += 10
            emp_biz_score += 5
        emp_count = app_data.get("numberOfEmployees") or ""
        if "100" in emp_count or "51" in emp_count:
            score += 15
            emp_biz_score += 8
        elif "26" in emp_count or "11" in emp_count:
            score += 8
            emp_biz_score += 4
    emp_biz_score = min(emp_biz_score, 95)

    # --- Debt Burden (5% weight) ---
    loan = app_data.get("loanAmount", 0) or 0
    debt_score = 75
    if app_type == "Individual":
        income_monthly = app_data.get("monthlyIncome", 1) or 1
        dti = loan / (income_monthly * 12)
        if dti < 2:
            debt_score = 85
        elif dti < 4:
            debt_score = 70
        else:
            debt_score = 55
    else:
        revenue = app_data.get("annualRevenue", 1) or 1
        loan_to_rev = loan / revenue
        if loan_to_rev < 0.5:
            debt_score = 85
        elif loan_to_rev < 1.5:
            debt_score = 70
        else:
            debt_score = 55

    # Clamp score
    score = min(max(score, 300), 975)

    # Determine category
    category = _get_category(score)
    cfg = SCORE_CONFIG[category]
    max_loan_key = "individual_max" if app_type == "Individual" else "sme_max"

    # Build strengths
    strengths = []
    if app_data.get("hasUtilityBills"):
        strengths.append("Regular utility bill payments on record")
    if app_data.get("hasUPIHistory"):
        strengths.append("Active digital payment trail via UPI")
    if app_data.get("hasBankAccount"):
        strengths.append("Verified bank account with transaction history")
    if app_type == "Individual":
        if (app_data.get("employmentType") or "").lower() == "salaried":
            strengths.append("Stable salaried employment — reduces income risk")
        qual = (app_data.get("qualification") or "").lower()
        if qual in ["postgraduate", "graduate", "professional"]:
            strengths.append("Higher education qualification improves profile")
    if app_type == "SME":
        if app_data.get("hasGSTReturns"):
            strengths.append("GST-compliant business with regular filings")
        if app_data.get("yearOfEstablishment") and (datetime.now().year - app_data["yearOfEstablishment"]) >= 3:
            strengths.append("Established business with proven vintage")
    if not strengths:
        strengths.append("Application submitted with multiple data points")

    # Build improvements
    improvements = []
    if not app_data.get("hasUtilityBills"):
        improvements.append("Add utility bill payment history to strengthen profile")
    if not app_data.get("hasUPIHistory"):
        improvements.append("Link UPI account to demonstrate digital payment activity")
    if not app_data.get("hasBankAccount"):
        improvements.append("Open and maintain a formal bank account")
    if app_type == "SME" and not app_data.get("hasGSTReturns"):
        improvements.append("File GST returns regularly to prove business compliance")
    if not improvements:
        improvements.append("Maintain consistency in all existing data sources")

    recommendations = [
        "Maintain at least 12 months of consistent payment records",
        "Keep bank account balance above ₹10,000 at month-end",
        "Ensure all mobile/utility bills are paid before due date",
    ]

    factors = [
        {
            "name": "Payment History",
            "score": payment_score,
            "weight": 35,
            "description": "Utility bills, rent payments, and recurring obligations",
        },
        {
            "name": "Income Stability",
            "score": income_score,
            "weight": 25,
            "description": "Employment consistency, revenue regularity, and income level",
        },
        {
            "name": "Alternative Data",
            "score": alt_score,
            "weight": 20,
            "description": "Digital footprint: UPI, bank activity, and online presence",
        },
        {
            "name": "Employment Profile" if app_type == "Individual" else "Business Profile",
            "score": emp_biz_score,
            "weight": 15,
            "description": "Work/business history, stability, and track record",
        },
        {
            "name": "Debt Burden",
            "score": debt_score,
            "weight": 5,
            "description": "Loan amount relative to income or revenue capacity",
        },
    ]

    coach_tips = _generate_coach_tips(factors, app_data, app_type)

    return {
        "creditScore": score,
        "riskCategory": category,
        "approvalStatus": cfg["status"],
        "interestRate": cfg["rate"],
        "maxLoanEligible": f"₹{cfg[max_loan_key]:,}",
        "factors": factors,
        "strengths": strengths,
        "improvements": improvements,
        "recommendations": recommendations,
        "coachTips": coach_tips,
        "aiConfidence": min(72 + (score - 300) // 15, 96),
        "modelUsed": "XGBoost ML Model" if USE_ML_MODEL else "Rule-Based Scoring Engine",
    }


def calculate_credit_score(app_data: dict, app_type: str) -> dict:
    """Route to ML model if loaded, else use rule-based engine."""
    if USE_ML_MODEL and ml_model is not None:
        try:
            from ml_models.feature_engineering import extract_features
            features = extract_features(app_data, app_type)
            score = int(ml_model.predict([features])[0])
            result = rule_based_score(app_data, app_type)
            result["creditScore"] = score
            result["riskCategory"] = _get_category(score)
            cfg = SCORE_CONFIG[result["riskCategory"]]
            max_loan_key = "individual_max" if app_type == "Individual" else "sme_max"
            result["approvalStatus"] = cfg["status"]
            result["interestRate"] = cfg["rate"]
            result["maxLoanEligible"] = f"₹{cfg[max_loan_key]:,}"
            result["modelUsed"] = "XGBoost ML Model"
            return result
        except Exception as e:
            print(f"ML inference failed, falling back to rule-based: {e}")

    return rule_based_score(app_data, app_type)


# ============================================================
# HELPER: Serialize ApplicationDB to dict
# ============================================================

def app_to_dict(app_rec: ApplicationDB) -> dict:
    return {
        "id": app_rec.id,
        "applicationType": app_rec.application_type,
        "applicantName": app_rec.applicant_name,
        "email": app_rec.email,
        "phone": app_rec.phone,
        "loanAmount": f"₹{int(app_rec.loan_amount):,}",
        "loanAmountRaw": app_rec.loan_amount,
        "loanPurpose": app_rec.loan_purpose,
        "creditScore": app_rec.credit_score,
        "riskCategory": app_rec.risk_category,
        "approvalStatus": app_rec.approval_status,
        "interestRate": app_rec.interest_rate,
        "maxLoanEligible": app_rec.max_loan_eligible,
        "status": app_rec.review_status,
        "aiConfidence": app_rec.ai_confidence,
        "modelUsed": app_rec.model_used,
        "submittedAt": app_rec.submitted_at.isoformat() if app_rec.submitted_at else None,
        "reviewedAt": app_rec.reviewed_at.isoformat() if app_rec.reviewed_at else None,
        "reviewedBy": app_rec.reviewed_by,
        "factors": json.loads(app_rec.factors_json or "[]"),
        "strengths": json.loads(app_rec.strengths_json or "[]"),
        "improvements": json.loads(app_rec.improvements_json or "[]"),
        "recommendations": json.loads(app_rec.recommendations_json or "[]"),
        "coachTips": json.loads(app_rec.coach_tips_json or "[]"),
    }


# ============================================================
# AUTH ENDPOINTS
# ============================================================

@app.post("/api/admin/token")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer", "username": ADMIN_USERNAME}


# ============================================================
# APPLICATION ENDPOINTS
# ============================================================

@app.post("/api/applications/individual")
def submit_individual(application: IndividualApplication, db: Session = Depends(get_db)):
    """Submit individual loan application."""
    try:
        app_id = f"IND-{uuid.uuid4().hex[:8].upper()}"
        app_data = application.model_dump()
        score_result = calculate_credit_score(app_data, "Individual")

        db_record = ApplicationDB(
            id=app_id,
            application_type="Individual",
            applicant_name=application.fullName,
            email=application.email,
            phone=application.mobileNumber,
            loan_amount=application.loanAmount,
            loan_purpose=application.loanPurpose,
            credit_score=score_result["creditScore"],
            risk_category=score_result["riskCategory"],
            approval_status=score_result["approvalStatus"],
            interest_rate=score_result["interestRate"],
            max_loan_eligible=score_result["maxLoanEligible"],
            review_status="pending",
            ai_confidence=score_result["aiConfidence"],
            model_used=score_result["modelUsed"],
            full_data_json=json.dumps(app_data),
            factors_json=json.dumps(score_result["factors"]),
            strengths_json=json.dumps(score_result["strengths"]),
            improvements_json=json.dumps(score_result["improvements"]),
            recommendations_json=json.dumps(score_result["recommendations"]),
            coach_tips_json=json.dumps(score_result.get("coachTips", [])),
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return {
            "applicationId": app_id,
            "applicationType": "Individual",
            "applicantName": application.fullName,
            "loanAmount": f"₹{int(application.loanAmount):,}",
            "submittedAt": db_record.submitted_at.isoformat(),
            "status": "success",
            **score_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process application. Please try again.")


@app.post("/api/applications/sme")
def submit_sme(application: SMEApplication, db: Session = Depends(get_db)):
    """Submit SME loan application."""
    try:
        app_id = f"SME-{uuid.uuid4().hex[:8].upper()}"
        app_data = application.model_dump()
        score_result = calculate_credit_score(app_data, "SME")

        db_record = ApplicationDB(
            id=app_id,
            application_type="SME",
            applicant_name=application.businessName,
            email=application.email,
            phone=application.mobileNumber,
            loan_amount=application.loanAmount,
            loan_purpose=application.loanPurpose,
            credit_score=score_result["creditScore"],
            risk_category=score_result["riskCategory"],
            approval_status=score_result["approvalStatus"],
            interest_rate=score_result["interestRate"],
            max_loan_eligible=score_result["maxLoanEligible"],
            review_status="pending",
            ai_confidence=score_result["aiConfidence"],
            model_used=score_result["modelUsed"],
            full_data_json=json.dumps(app_data),
            factors_json=json.dumps(score_result["factors"]),
            strengths_json=json.dumps(score_result["strengths"]),
            improvements_json=json.dumps(score_result["improvements"]),
            recommendations_json=json.dumps(score_result["recommendations"]),
            coach_tips_json=json.dumps(score_result.get("coachTips", [])),
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return {
            "applicationId": app_id,
            "applicationType": "SME",
            "applicantName": application.businessName,
            "loanAmount": f"₹{int(application.loanAmount):,}",
            "submittedAt": db_record.submitted_at.isoformat(),
            "status": "success",
            **score_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process application. Please try again.")


@app.get("/api/applications/{application_id}")
def get_application(application_id: str, db: Session = Depends(get_db)):
    """Get application by ID — used for public tracking."""
    app_rec = db.query(ApplicationDB).filter(ApplicationDB.id == application_id).first()
    if not app_rec:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
    return app_to_dict(app_rec)


# ============================================================
# ADMIN ENDPOINTS (JWT Protected)
# ============================================================

@app.get("/api/admin/applications")
def get_all_applications(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    app_type: Optional[str] = None,
    review_status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Admin: list all applications with filtering and pagination."""
    query = db.query(ApplicationDB)

    if search:
        query = query.filter(
            (ApplicationDB.applicant_name.ilike(f"%{search}%")) |
            (ApplicationDB.id.ilike(f"%{search}%")) |
            (ApplicationDB.email.ilike(f"%{search}%"))
        )
    if app_type and app_type != "all":
        query = query.filter(ApplicationDB.application_type == app_type)
    if review_status and review_status != "all":
        query = query.filter(ApplicationDB.review_status == review_status)

    total = query.count()
    records = query.order_by(ApplicationDB.submitted_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "applications": [app_to_dict(r) for r in records],
    }


@app.put("/api/admin/applications/{application_id}/review")
def review_application(
    application_id: str,
    action_req: AdminActionRequest,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Admin: approve or reject an application."""
    app_rec = db.query(ApplicationDB).filter(ApplicationDB.id == application_id).first()
    if not app_rec:
        raise HTTPException(status_code=404, detail="Application not found")

    if action_req.action not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    app_rec.review_status = action_req.action
    app_rec.reviewed_at = datetime.utcnow()
    app_rec.reviewed_by = admin_user
    db.commit()

    return {"success": True, "applicationId": application_id, "newStatus": action_req.action}


@app.get("/api/admin/stats")
def get_stats(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    """Admin: real statistics from database."""
    all_apps = db.query(ApplicationDB).all()

    if not all_apps:
        return {
            "totalApplications": 0,
            "approvedApplications": 0,
            "pendingApplications": 0,
            "rejectedApplications": 0,
            "averageScore": 0,
            "totalDisbursed": "₹0",
            "approvalRate": 0,
            "avgProcessingTime": "< 1 min",
            "individualCount": 0,
            "smeCount": 0,
            "riskDistribution": {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0},
        }

    total = len(all_apps)
    approved = sum(1 for a in all_apps if a.review_status == "approved")
    pending = sum(1 for a in all_apps if a.review_status == "pending")
    rejected = sum(1 for a in all_apps if a.review_status == "rejected")
    avg_score = int(sum(a.credit_score for a in all_apps) / total)
    total_disbursed = sum(a.loan_amount for a in all_apps if a.review_status == "approved")
    individual_count = sum(1 for a in all_apps if a.application_type == "Individual")
    sme_count = sum(1 for a in all_apps if a.application_type == "SME")

    risk_dist = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0}
    for a in all_apps:
        if a.risk_category in risk_dist:
            risk_dist[a.risk_category] += 1

    if total_disbursed >= 10000000:
        disbursed_str = f"₹{total_disbursed/10000000:.1f} Cr"
    elif total_disbursed >= 100000:
        disbursed_str = f"₹{total_disbursed/100000:.1f} L"
    else:
        disbursed_str = f"₹{int(total_disbursed):,}"

    return {
        "totalApplications": total,
        "approvedApplications": approved,
        "pendingApplications": pending,
        "rejectedApplications": rejected,
        "averageScore": avg_score,
        "totalDisbursed": disbursed_str,
        "approvalRate": round((approved / total * 100), 1) if total > 0 else 0,
        "avgProcessingTime": "< 1 min",
        "individualCount": individual_count,
        "smeCount": sme_count,
        "riskDistribution": risk_dist,
    }


# ============================================================
# PUBLIC ENDPOINTS
# ============================================================

@app.get("/")
def read_root():
    return {
        "product": "Crededge",
        "description": "AI Credit Risk Assessment for Underserved Segments",
        "version": "2.0.0",
        "engine": "XGBoost ML" if USE_ML_MODEL else "Rule-Based Scoring",
        "docs": "/docs",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {
        "status": "healthy",
        "database": db_status,
        "model": "ML" if USE_ML_MODEL else "Rule-Based",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Crededge API v2.0 starting...")
    print(f"  Scoring Engine: {'XGBoost ML Model' if USE_ML_MODEL else 'Rule-Based Engine'}")
    print(f"  Database: {DATABASE_URL}")
    print("  Docs: http://localhost:8000/docs")
    print("  Frontend: http://localhost:3000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
