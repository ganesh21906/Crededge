"""
Crededge — Engines Router
All engine-specific endpoints: psychometric quiz, document upload, AA flow, engine status.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from dependencies import get_db, get_current_admin
from schemas.application import PsychometricSubmission
import services.psychometric_service    as psych_svc
import services.bank_statement_service  as bank_svc
import services.ocr_service             as ocr_svc
import services.aa_service              as aa_svc
import services.application_service     as app_svc

router = APIRouter(prefix="/api/engines", tags=["engines"])


# ── Engine Catalogue ─────────────────────────────────────────

ENGINES = [
    {
        "id":          "rule_engine",
        "name":        "Rule-Based Scoring Engine",
        "icon":        "⚡",
        "status":      "active",
        "category":    "Core",
        "description": "Deterministic rule-based credit scoring using 5 weighted factors: payment history, income stability, alternative data, employment profile, and debt burden.",
        "maxBonus":    475,
        "requirements": [
            {"signal": "Monthly income > ₹30,000",     "points": "+35"},
            {"signal": "Salaried employment",           "points": "+45"},
            {"signal": "2+ years work experience",      "points": "+15"},
            {"signal": "Utility bills on record",       "points": "+50"},
            {"signal": "Active UPI history",            "points": "+40"},
            {"signal": "Bank account with balance",     "points": "+20 to +50"},
        ],
    },
    {
        "id":          "fraud_detection",
        "name":        "Fraud & Anomaly Detection",
        "icon":        "🛡️",
        "status":      "active",
        "category":    "Risk",
        "description": "Multi-layer anomaly detection: income-lifestyle mismatch, round-number heuristics, extreme DTI ratios, phone duplication check, and document consistency validation.",
        "maxBonus":    0,
        "maxPenalty":  -50,
        "requirements": [
            {"signal": "Income consistent with lifestyle",   "points": "No penalty"},
            {"signal": "No duplicate phone/email in DB",     "points": "No penalty"},
            {"signal": "Loan-to-income ratio < 5x",          "points": "No penalty"},
            {"signal": "Valid PAN/GST format",               "points": "No penalty"},
            {"signal": "Revenue figures internally consistent", "points": "No penalty"},
        ],
    },
    {
        "id":          "psychometric",
        "name":        "Psychometric Assessment Engine",
        "icon":        "🧠",
        "status":      "active",
        "category":    "Behavioral",
        "description": "15-question behavioral assessment measuring Financial IQ, Future Orientation, Risk Attitude, and Integrity. Harvard-validated methodology used in microfinance globally.",
        "maxBonus":    60,
        "requirements": [
            {"signal": "Complete all 15 questions",     "points": "Required"},
            {"signal": "Financial IQ > 70%",            "points": "+20 to +25"},
            {"signal": "Future orientation score",      "points": "+15 to +18"},
            {"signal": "Risk attitude (balanced)",      "points": "+8 to +12"},
            {"signal": "Integrity & consistency",       "points": "+5 to +8"},
        ],
    },
    {
        "id":          "explainability",
        "name":        "AI Explainability (SHAP Waterfall)",
        "icon":        "📊",
        "status":      "active",
        "category":    "Transparency",
        "description": "SHAP-style factor contribution waterfall showing exactly how much each data point added or removed from the final score. Makes AI decisions fully transparent to applicants and lenders.",
        "maxBonus":    0,
        "requirements": [
            {"signal": "Auto-generated for all applications", "points": "Informational"},
            {"signal": "Top 10 factors shown",               "points": "Informational"},
            {"signal": "Plain language explanations",        "points": "Informational"},
        ],
    },
    {
        "id":          "peer_benchmark",
        "name":        "Peer Benchmarking Engine",
        "icon":        "📈",
        "status":      "active",
        "category":    "Analytics",
        "description": "Compares each applicant against a cohort of similar profiles in the database. Provides percentile position and motivational context message.",
        "maxBonus":    0,
        "requirements": [
            {"signal": "Min 3 similar applicants in DB",    "points": "For benchmark to show"},
            {"signal": "Similar employment type",           "points": "Matching criteria"},
            {"signal": "Similar income band (±40%)",        "points": "Matching criteria"},
        ],
    },
    {
        "id":          "bank_statement",
        "name":        "Bank Statement Cash Flow Analyzer",
        "icon":        "🏦",
        "status":      "active",
        "category":    "Document",
        "description": "Upload 6-12 month bank statement PDF. Extracts: income regularity, savings rate, average balance, dishonored cheques, EMI patterns, and UPI usage frequency.",
        "maxBonus":    120,
        "requirements": [
            {"signal": "Upload 6+ month bank statement PDF",     "points": "Required"},
            {"signal": "Regular salary credits",                 "points": "+15"},
            {"signal": "Savings rate > 20%",                     "points": "+15"},
            {"signal": "Average balance > ₹50,000",              "points": "+10"},
            {"signal": "Zero dishonored cheques",                "points": "Prerequisite"},
            {"signal": "Install pdfplumber for full parsing",     "points": "Recommended"},
        ],
    },
    {
        "id":          "ocr_document",
        "name":        "OCR Document Intelligence",
        "icon":        "📄",
        "status":      "active",
        "category":    "Document",
        "description": "AI-powered OCR verification of utility bills, ITR, GST returns, MSME certificates, salary slips, and rental agreements. Extracts structured data automatically.",
        "maxBonus":    80,
        "requirements": [
            {"signal": "Upload ITR acknowledgement PDF",       "points": "+45"},
            {"signal": "Upload GST return PDF",                "points": "+50"},
            {"signal": "Upload utility bill (6 months)",       "points": "+35"},
            {"signal": "Upload MSME certificate",              "points": "+40"},
            {"signal": "Upload salary slip",                   "points": "+30"},
            {"signal": "Upload rental agreement",              "points": "+25"},
        ],
    },
    {
        "id":          "account_aggregator",
        "name":        "Account Aggregator (RBI AA Framework)",
        "icon":        "🔗",
        "status":      "beta",
        "category":    "Open Finance",
        "description": "RBI-approved consent-based real-time bank data fetching. Fetches 12-month transaction history directly from nationalized banks with user consent. Most powerful alternative data source.",
        "maxBonus":    100,
        "requirements": [
            {"signal": "User gives consent on AA app",          "points": "Required"},
            {"signal": "12 months bank data fetched",           "points": "+40"},
            {"signal": "6+ salary credits in 12 months",        "points": "+30"},
            {"signal": "Zero dishonored cheques",               "points": "+20"},
            {"signal": "Savings rate > 15%",                    "points": "+10"},
            {"signal": "Average balance > ₹20,000",             "points": "+10"},
        ],
    },
]


@router.get("/status")
def get_engines_status():
    """Return the catalogue of all 7 engines with their status and requirements."""
    return {
        "engines":       ENGINES,
        "totalEngines":  len(ENGINES),
        "activeEngines": sum(1 for e in ENGINES if e["status"] == "active"),
        "maxTotalScore": 975,
        "baselineScore": 500,
        "maxBonus":      sum(e.get("maxBonus", 0) for e in ENGINES),
    }


# ── Psychometric Endpoints ─────────────────────────────────────

@router.get("/psychometric/questions")
def get_psychometric_questions():
    """Return all 15 quiz questions (without scoring metadata)."""
    return {
        "questions": psych_svc.get_questions(),
        "totalQuestions": len(psych_svc.QUESTIONS),
        "estimatedMinutes": 5,
        "maxBonus": 60,
        "categories": ["Financial IQ", "Future Orientation", "Risk Attitude", "Integrity"],
    }


@router.post("/psychometric/submit")
def submit_psychometric(
    submission: PsychometricSubmission,
    db: Session = Depends(get_db),
):
    """Score psychometric responses and apply bonus to existing application."""
    result = psych_svc.score_responses(submission.responses)
    return app_svc.apply_psychometric_bonus(submission.applicationId, result, db)


# ── Bank Statement Upload ──────────────────────────────────────

@router.post("/bank-statement/{application_id}")
async def upload_bank_statement(
    application_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a bank statement PDF for cash flow analysis."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    content = await file.read()
    result  = bank_svc.analyze_bank_statement(content, file.filename)
    return app_svc.apply_bank_statement_bonus(application_id, result, db)


# ── Document Upload (OCR) ─────────────────────────────────────

@router.post("/documents/{application_id}")
async def upload_document(
    application_id: str,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a document for OCR verification (utility bill, ITR, GST, etc.)."""
    content      = await file.read()
    ocr_result   = ocr_svc.verify_document(content, file.filename, doc_type)
    bonus_result = app_svc.apply_ocr_bonus(application_id, [ocr_result], db)
    return {**ocr_result, **bonus_result}


@router.get("/documents/types")
def get_document_types():
    """Return list of supported document types with bonus values."""
    return {"documentTypes": ocr_svc.get_supported_document_types()}


# ── Account Aggregator ────────────────────────────────────────

@router.post("/aa/initiate/{application_id}")
def initiate_aa_consent(
    application_id: str,
    user_phone: str,
    db: Session = Depends(get_db),
):
    """Initiate AA consent request. Returns URL to redirect user to AA app."""
    return aa_svc.create_consent_request(application_id, user_phone)


@router.post("/aa/simulate-approve/{consent_handle}")
def simulate_aa_approval(
    consent_handle: str,
    application_id: str,
    db: Session = Depends(get_db),
):
    """Simulate AA consent approval (demo). In production: triggered by webhook."""
    result = aa_svc.simulate_consent_approval(consent_handle)
    if result.get("success"):
        return app_svc.apply_aa_bonus(application_id, result, db)
    raise HTTPException(status_code=400, detail=result.get("error", "AA simulation failed"))


@router.get("/aa/status/{consent_handle}")
def get_aa_status(consent_handle: str):
    """Check current status of an AA consent request."""
    return aa_svc.get_aa_status(consent_handle)


# ── Score Architecture (for dashboard display) ─────────────────

@router.get("/score-architecture")
def get_score_architecture():
    """Return the full score architecture used in all applications."""
    return {
        "baseline": 500,
        "maxScore": 975,
        "tiers": [
            {"name": "Excellent", "min": 850, "max": 975, "color": "#10b981",
             "interestRate": "10.5%", "individualMax": "₹5,00,000", "smeMax": "₹25,00,000",
             "approval": "Auto-Approved"},
            {"name": "Good",      "min": 750, "max": 849, "color": "#3b82f6",
             "interestRate": "12.5%", "individualMax": "₹3,50,000", "smeMax": "₹18,00,000",
             "approval": "Approved"},
            {"name": "Fair",      "min": 650, "max": 749, "color": "#f59e0b",
             "interestRate": "15.0%", "individualMax": "₹2,00,000", "smeMax": "₹12,00,000",
             "approval": "Under Review"},
            {"name": "Poor",      "min": 300, "max": 649, "color": "#ef4444",
             "interestRate": "18.0%", "individualMax": "₹1,00,000", "smeMax": "₹8,00,000",
             "approval": "Requires Additional Review"},
        ],
        "engineContributions": [
            {"engine": "Rule-Based Engine",  "maxPoints": 475, "auto": True},
            {"engine": "Psychometric Quiz",  "maxPoints": 60,  "auto": False, "optional": True},
            {"engine": "Bank Statement",     "maxPoints": 120, "auto": False, "optional": True},
            {"engine": "OCR Documents",      "maxPoints": 80,  "auto": False, "optional": True},
            {"engine": "Account Aggregator", "maxPoints": 100, "auto": False, "optional": True},
            {"engine": "Fraud Detection",    "maxPoints": 0,   "maxPenalty": -50, "auto": True},
        ],
    }
