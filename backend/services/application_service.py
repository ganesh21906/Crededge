"""
Crededge — Application Service (v2 — 7-Engine Pipeline)
Orchestrates all scoring engines for every application submission.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.application import Application
from schemas.application import (
    IndividualApplication, SMEApplication,
    ApplicationSummary, ApplicationListResponse,
    ApplicationResponse, AdminStatsResponse,
)
from services.scoring_service       import calculate_credit_score
from services.fraud_service         import analyze_fraud
from services.explainability_service import generate_waterfall
from services.peer_service          import get_peer_benchmark

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# SERIALIZATION
# ────────────────────────────────────────────────────────────

def _record_to_summary(rec: Application) -> ApplicationSummary:
    return ApplicationSummary(
        id=rec.id,
        applicationType=rec.application_type,
        applicantName=rec.applicant_name,
        email=rec.email,
        phone=rec.phone,
        loanAmount=f"₹{int(rec.loan_amount):,}",
        loanAmountRaw=rec.loan_amount,
        loanPurpose=rec.loan_purpose,
        creditScore=rec.credit_score,
        riskCategory=rec.risk_category,
        approvalStatus=rec.approval_status,
        interestRate=rec.interest_rate,
        maxLoanEligible=rec.max_loan_eligible,
        status=rec.review_status,
        aiConfidence=rec.ai_confidence or 0.0,
        modelUsed=rec.model_used,
        submittedAt=rec.submitted_at.isoformat() if rec.submitted_at else None,
        reviewedAt=rec.reviewed_at.isoformat() if rec.reviewed_at else None,
        reviewedBy=rec.reviewed_by,
        factors=json.loads(rec.factors_json or "[]"),
        strengths=json.loads(rec.strengths_json or "[]"),
        improvements=json.loads(rec.improvements_json or "[]"),
        recommendations=json.loads(rec.recommendations_json or "[]"),
        coachTips=json.loads(rec.coach_tips_json or "[]"),
        # Engine results
        fraudRisk=rec.fraud_risk or "Low",
        fraudFlags=json.loads(rec.fraud_flags_json or "[]"),
        fraudScore=rec.fraud_score or 100,
        psychometricScore=rec.psychometric_score,
        psychometricBonus=rec.psychometric_bonus or 0,
        psychometricCompleted=bool(rec.psychometric_completed),
        shapWaterfall=json.loads(rec.shap_waterfall_json or "[]"),
        peerPercentile=rec.peer_percentile,
        peerAvgScore=rec.peer_avg_score,
        peerCount=rec.peer_count,
        peerGroupLabel=rec.peer_group_label,
        bankStatementUploaded=bool(rec.bank_statement_uploaded),
        bankStatementScore=rec.bank_statement_score,
        bankStatementBonus=rec.bank_statement_bonus or 0,
        ocrDocsVerified=rec.ocr_docs_verified or 0,
        ocrBonus=rec.ocr_bonus or 0,
        aaVerified=bool(rec.aa_verified),
        aaBonus=rec.aa_bonus or 0,
        engineContributions=json.loads(rec.engine_contributions_json or "{}"),
    )


# ────────────────────────────────────────────────────────────
# ENGINE PIPELINE
# ────────────────────────────────────────────────────────────

def _run_all_engines(app_data: dict, app_type: str, base_score: int, db: Session) -> dict:
    """Run all available engines and return enriched score + metadata."""

    # Engine 1: Fraud Detection
    fraud = analyze_fraud(app_data, app_type, db)

    # Engine 3: SHAP Waterfall (Explainability)
    waterfall = generate_waterfall(app_data, app_type, base_score, base_score)

    # Engine 4: Peer Benchmarking
    peer = get_peer_benchmark(app_data, app_type, base_score, db)

    # Engine contributions (what each engine added at initial submission)
    contributions = {
        "Rule-Based Engine": base_score - 500,  # vs baseline
        "Fraud Detection":   0,  # No bonus — this is a risk flag engine
        "Psychometric":      0,  # Added after quiz completion
        "Bank Statement":    0,  # Added after upload
        "OCR Verify":        0,  # Added after upload
        "AA Framework":      0,  # Added after consent
        "Peer Benchmark":    0,  # Informational only
    }

    # Fraud penalty: High fraud risk reduces final score
    fraud_penalty = 0
    if fraud["fraudRisk"] == "High":
        fraud_penalty = 50
        contributions["Fraud Detection"] = -50
    elif fraud["fraudRisk"] == "Medium":
        fraud_penalty = 20
        contributions["Fraud Detection"] = -20

    adjusted_score = max(300, base_score - fraud_penalty)

    return {
        "finalScore":    adjusted_score,
        "fraudResult":   fraud,
        "waterfall":     waterfall,
        "peer":          peer,
        "contributions": contributions,
    }


# ────────────────────────────────────────────────────────────
# WRITE OPERATIONS
# ────────────────────────────────────────────────────────────

def _build_record(app_id, app_type, name, email, phone, loan_amount, loan_purpose,
                  score_result, engine_result, app_data) -> Application:
    """Assemble the full Application ORM record from all engine results."""
    fraud   = engine_result["fraudResult"]
    peer    = engine_result["peer"]

    return Application(
        id=app_id,
        application_type=app_type,
        applicant_name=name,
        email=email,
        phone=phone,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        credit_score=engine_result["finalScore"],
        risk_category=score_result["riskCategory"],
        approval_status=score_result["approvalStatus"],
        interest_rate=score_result["interestRate"],
        max_loan_eligible=score_result["maxLoanEligible"],
        ai_confidence=score_result["aiConfidence"],
        model_used=score_result["modelUsed"],
        review_status="under_review" if fraud.get("autoReview") else "pending",
        full_data_json=json.dumps(app_data),
        factors_json=json.dumps(score_result["factors"]),
        strengths_json=json.dumps(score_result["strengths"]),
        improvements_json=json.dumps(score_result["improvements"]),
        recommendations_json=json.dumps(score_result["recommendations"]),
        coach_tips_json=json.dumps(score_result.get("coachTips", [])),
        # Engine 1: Fraud
        fraud_risk=fraud["fraudRisk"],
        fraud_flags_json=json.dumps(fraud["fraudFlags"]),
        fraud_score=fraud["fraudScore"],
        # Engine 3: SHAP
        shap_waterfall_json=json.dumps(engine_result["waterfall"]),
        # Engine 4: Peer
        peer_percentile=peer.get("yourPercentile") if peer.get("available") else None,
        peer_avg_score=peer.get("peerAvgScore") if peer.get("available") else None,
        peer_count=peer.get("peerCount") if peer.get("available") else None,
        peer_group_label=peer.get("groupLabel") if peer.get("available") else None,
        # Engine contributions
        engine_contributions_json=json.dumps(engine_result["contributions"]),
    )


def create_individual_application(application: IndividualApplication, db: Session) -> ApplicationResponse:
    app_id   = f"IND-{uuid.uuid4().hex[:8].upper()}"
    app_data = application.model_dump()

    score_result   = calculate_credit_score(app_data, "Individual")
    engine_result  = _run_all_engines(app_data, "Individual", score_result["creditScore"], db)
    score_result["creditScore"] = engine_result["finalScore"]

    record = _build_record(
        app_id, "Individual", application.fullName, application.email,
        application.mobileNumber, application.loanAmount, application.loanPurpose,
        score_result, engine_result, app_data,
    )
    db.add(record); db.commit(); db.refresh(record)

    peer = engine_result["peer"]
    return ApplicationResponse(
        applicationId=app_id, applicationType="Individual",
        applicantName=application.fullName,
        loanAmount=f"₹{int(application.loanAmount):,}",
        submittedAt=record.submitted_at.isoformat(),
        fraudRisk=engine_result["fraudResult"]["fraudRisk"],
        fraudFlags=engine_result["fraudResult"]["fraudFlags"],
        shapWaterfall=engine_result["waterfall"],
        peerBenchmark=peer if peer.get("available") else None,
        engineContributions=engine_result["contributions"],
        **{k: v for k, v in score_result.items() if k != "creditScore"},
        creditScore=engine_result["finalScore"],
    )


def create_sme_application(application: SMEApplication, db: Session) -> ApplicationResponse:
    app_id   = f"SME-{uuid.uuid4().hex[:8].upper()}"
    app_data = application.model_dump()

    score_result   = calculate_credit_score(app_data, "SME")
    engine_result  = _run_all_engines(app_data, "SME", score_result["creditScore"], db)
    score_result["creditScore"] = engine_result["finalScore"]

    record = _build_record(
        app_id, "SME", application.businessName, application.email,
        application.mobileNumber, application.loanAmount, application.loanPurpose,
        score_result, engine_result, app_data,
    )
    db.add(record); db.commit(); db.refresh(record)

    peer = engine_result["peer"]
    return ApplicationResponse(
        applicationId=app_id, applicationType="SME",
        applicantName=application.businessName,
        loanAmount=f"₹{int(application.loanAmount):,}",
        submittedAt=record.submitted_at.isoformat(),
        fraudRisk=engine_result["fraudResult"]["fraudRisk"],
        fraudFlags=engine_result["fraudResult"]["fraudFlags"],
        shapWaterfall=engine_result["waterfall"],
        peerBenchmark=peer if peer.get("available") else None,
        engineContributions=engine_result["contributions"],
        **{k: v for k, v in score_result.items() if k != "creditScore"},
        creditScore=engine_result["finalScore"],
    )


# ────────────────────────────────────────────────────────────
# ENGINE UPDATES (called by separate endpoints)
# ────────────────────────────────────────────────────────────

def apply_psychometric_bonus(application_id: str, psych_result: dict, db: Session) -> dict:
    """Update application score after psychometric quiz completion."""
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Application not found")

    bonus = psych_result["psychometricBonus"]
    rec.psychometric_score       = psych_result["psychometricScore"]
    rec.psychometric_bonus       = bonus
    rec.psychometric_completed   = 1
    rec.psychometric_breakdown_json = json.dumps(psych_result.get("breakdown", {}))
    rec.credit_score             = min(975, rec.credit_score + bonus)

    # Update engine contributions
    contributions = json.loads(rec.engine_contributions_json or "{}")
    contributions["Psychometric"] = bonus
    rec.engine_contributions_json = json.dumps(contributions)

    db.commit()
    return {
        "applicationId": application_id,
        "newScore":      rec.credit_score,
        "bonusAdded":    bonus,
        "psychometricScore": psych_result["psychometricScore"],
        "breakdown":     psych_result.get("breakdown", {}),
    }


def apply_bank_statement_bonus(application_id: str, bs_result: dict, db: Session) -> dict:
    """Update application score after bank statement analysis."""
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Application not found")

    bonus = bs_result.get("bankStatementBonus", 0)
    rec.bank_statement_uploaded = 1
    rec.bank_statement_score    = bs_result.get("bankStatementScore", 0)
    rec.bank_statement_bonus    = bonus
    rec.bank_cash_flow_json     = json.dumps(bs_result.get("cashFlow", {}))
    rec.credit_score            = min(975, rec.credit_score + bonus)

    contributions = json.loads(rec.engine_contributions_json or "{}")
    contributions["Bank Statement"] = bonus
    rec.engine_contributions_json = json.dumps(contributions)

    db.commit()
    return {"applicationId": application_id, "newScore": rec.credit_score, "bonusAdded": bonus}


def apply_ocr_bonus(application_id: str, ocr_results: list, db: Session) -> dict:
    """Update application score after document verification."""
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Application not found")

    total_bonus   = sum(r.get("bonusPoints", 0) for r in ocr_results if r.get("verified"))
    verified_docs = [r["docType"] for r in ocr_results if r.get("verified")]

    rec.ocr_docs_verified    = len(verified_docs)
    rec.ocr_bonus            = total_bonus
    rec.ocr_verified_list_json = json.dumps(verified_docs)
    rec.credit_score         = min(975, rec.credit_score + total_bonus)

    contributions = json.loads(rec.engine_contributions_json or "{}")
    contributions["OCR Verify"] = total_bonus
    rec.engine_contributions_json = json.dumps(contributions)

    db.commit()
    return {"applicationId": application_id, "newScore": rec.credit_score, "bonusAdded": total_bonus, "verifiedDocs": verified_docs}


def apply_aa_bonus(application_id: str, aa_result: dict, db: Session) -> dict:
    """Update application score after AA verification."""
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Application not found")

    bonus = aa_result.get("aaBonus", 0)
    rec.aa_verified        = 1
    rec.aa_bonus           = bonus
    rec.aa_verified_income = aa_result.get("aaVerifiedIncome")
    rec.credit_score       = min(975, rec.credit_score + bonus)

    contributions = json.loads(rec.engine_contributions_json or "{}")
    contributions["AA Framework"] = bonus
    rec.engine_contributions_json = json.dumps(contributions)

    db.commit()
    return {"applicationId": application_id, "newScore": rec.credit_score, "bonusAdded": bonus}


# ────────────────────────────────────────────────────────────
# READ OPERATIONS
# ────────────────────────────────────────────────────────────

def get_application_by_id(application_id: str, db: Session) -> ApplicationSummary:
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Application '{application_id}' not found")
    return _record_to_summary(rec)


def list_applications(db, skip=0, limit=20, search=None, app_type=None, review_status=None):
    from schemas.application import ApplicationListResponse
    query = db.query(Application)
    if search:
        query = query.filter(
            Application.applicant_name.ilike(f"%{search}%") |
            Application.id.ilike(f"%{search}%") |
            Application.email.ilike(f"%{search}%")
        )
    if app_type and app_type != "all":
        query = query.filter(Application.application_type == app_type)
    if review_status and review_status != "all":
        query = query.filter(Application.review_status == review_status)
    total   = query.count()
    records = query.order_by(Application.submitted_at.desc()).offset(skip).limit(limit).all()
    return ApplicationListResponse(total=total, skip=skip, limit=limit,
                                   applications=[_record_to_summary(r) for r in records])


def review_application(application_id, action, admin_user, db):
    if action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")
    rec = db.query(Application).filter(Application.id == application_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Application not found")
    rec.review_status = action
    rec.reviewed_at   = datetime.utcnow()
    rec.reviewed_by   = admin_user
    db.commit()
    return {"success": True, "applicationId": application_id, "newStatus": action}


def get_admin_stats(db: Session):
    from schemas.application import AdminStatsResponse
    all_apps = db.query(Application).all()
    if not all_apps:
        return AdminStatsResponse(
            totalApplications=0, approvedApplications=0, pendingApplications=0,
            rejectedApplications=0, averageScore=0, totalDisbursed="₹0",
            approvalRate=0.0, avgProcessingTime="< 1 min", individualCount=0,
            smeCount=0, riskDistribution={"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0},
            fraudHighCount=0, fraudMediumCount=0, psychometricCompletedCount=0,
            bankStatementCount=0, aaVerifiedCount=0, enginePerformance={},
        )

    total    = len(all_apps)
    approved = sum(1 for a in all_apps if a.review_status == "approved")
    pending  = sum(1 for a in all_apps if a.review_status in ("pending", "under_review"))
    rejected = sum(1 for a in all_apps if a.review_status == "rejected")
    avg_score = int(sum(a.credit_score for a in all_apps) / total)
    distributed = sum(a.loan_amount for a in all_apps if a.review_status == "approved")

    risk_dist: dict = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0}
    for a in all_apps:
        if a.risk_category in risk_dist:
            risk_dist[a.risk_category] += 1

    disbursed_str = (
        f"₹{distributed/10_000_000:.1f} Cr" if distributed >= 10_000_000
        else f"₹{distributed/100_000:.1f} L" if distributed >= 100_000
        else f"₹{int(distributed):,}"
    )

    # Engine performance stats
    psych_completed  = sum(1 for a in all_apps if a.psychometric_completed)
    bank_uploaded    = sum(1 for a in all_apps if a.bank_statement_uploaded)
    aa_verified      = sum(1 for a in all_apps if a.aa_verified)
    fraud_high       = sum(1 for a in all_apps if a.fraud_risk == "High")
    fraud_medium     = sum(1 for a in all_apps if a.fraud_risk == "Medium")

    avg_psych_bonus  = int(sum(a.psychometric_bonus or 0 for a in all_apps) / total)
    avg_bank_bonus   = int(sum(a.bank_statement_bonus or 0 for a in all_apps) / total)
    avg_ocr_bonus    = int(sum(a.ocr_bonus or 0 for a in all_apps) / total)
    avg_aa_bonus     = int(sum(a.aa_bonus or 0 for a in all_apps) / total)

    return AdminStatsResponse(
        totalApplications=total, approvedApplications=approved,
        pendingApplications=pending, rejectedApplications=rejected,
        averageScore=avg_score, totalDisbursed=disbursed_str,
        approvalRate=round(approved / total * 100, 1) if total else 0.0,
        avgProcessingTime="< 1 min",
        individualCount=sum(1 for a in all_apps if a.application_type == "Individual"),
        smeCount=sum(1 for a in all_apps if a.application_type == "SME"),
        riskDistribution=risk_dist,
        fraudHighCount=fraud_high, fraudMediumCount=fraud_medium,
        psychometricCompletedCount=psych_completed,
        bankStatementCount=bank_uploaded, aaVerifiedCount=aa_verified,
        enginePerformance={
            "Psychometric":   {"count": psych_completed, "avgBonus": avg_psych_bonus},
            "Bank Statement": {"count": bank_uploaded,   "avgBonus": avg_bank_bonus},
            "OCR Verify":     {"count": 0,               "avgBonus": avg_ocr_bonus},
            "AA Framework":   {"count": aa_verified,     "avgBonus": avg_aa_bonus},
        },
    )
