"""
Crededge — Scoring Service
Pure business logic: no FastAPI, no SQLAlchemy, no HTTP concerns.
Receives a dict of applicant data, returns a structured score result dict.

Entry point: calculate_credit_score(app_data, app_type) -> dict
"""

import logging
from datetime import datetime
from typing import Optional

from config import settings
from ml.model_loader import get_model

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# SCORE CONFIG  (built from settings — single source of truth)
# ────────────────────────────────────────────────────────────

def _build_score_config() -> dict:
    s = settings
    return {
        "Excellent": {
            "rate": s.rate_excellent,
            "individual_max": s.individual_max_excellent,
            "sme_max":        s.sme_max_excellent,
            "approval":       "Approved",
        },
        "Good": {
            "rate": s.rate_good,
            "individual_max": s.individual_max_good,
            "sme_max":        s.sme_max_good,
            "approval":       "Approved",
        },
        "Fair": {
            "rate": s.rate_fair,
            "individual_max": s.individual_max_fair,
            "sme_max":        s.sme_max_fair,
            "approval":       "Under Review",
        },
        "Poor": {
            "rate": s.rate_poor,
            "individual_max": s.individual_max_poor,
            "sme_max":        s.sme_max_poor,
            "approval":       "Requires Additional Review",
        },
    }


# ────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ────────────────────────────────────────────────────────────

def _get_category(score: int) -> str:
    if score >= settings.threshold_excellent:
        return "Excellent"
    if score >= settings.threshold_good:
        return "Good"
    if score >= settings.threshold_fair:
        return "Fair"
    return "Poor"


def _fmt_inr(amount: int) -> str:
    return f"₹{amount:,}"


# ────────────────────────────────────────────────────────────
# AI FINANCIAL COACH
# ────────────────────────────────────────────────────────────

def _generate_coach_tips(factors: list, app_data: dict, app_type: str) -> list:
    """
    Rule-based, data-driven improvement tips.
    Each tip is personalized to the applicant's actual submitted values.
    Returns at most 5 ranked tips.
    """
    tips = []
    factor_map = {f["name"]: f["score"] for f in factors}

    if factor_map.get("Payment History", 100) < 80:
        tips.append({
            "icon": "💡",
            "title": "Pay Bills Consistently",
            "tip": "Paying electricity, water, and mobile bills on time every month can add +40 to +60 points within 6 months.",
            "impact": "High",
            "timeframe": "6 months",
        })

    if factor_map.get("Alternative Data", 100) < 80:
        tips.append({
            "icon": "📱",
            "title": "Activate UPI Payments",
            "tip": "Regular UPI transactions (10+ per month) demonstrate financial activity and can boost your score by +30 to +50 points.",
            "impact": "High",
            "timeframe": "3 months",
        })

    if factor_map.get("Income Stability", 100) < 75:
        tips.append({
            "icon": "💰",
            "title": "Stabilize Your Income",
            "tip": "Consistent income credited to the same bank account for 3+ consecutive months significantly improves income stability score.",
            "impact": "Very High",
            "timeframe": "3-6 months",
        })

    if not app_data.get("hasBankAccount"):
        tips.append({
            "icon": "🏦",
            "title": "Open a Bank Account",
            "tip": "A formal bank account is the foundation of credit history. Open one today and maintain a minimum balance of ₹5,000.",
            "impact": "Very High",
            "timeframe": "Immediate",
        })

    if app_type == "Individual" and not app_data.get("hasRentalAgreement"):
        tips.append({
            "icon": "🏠",
            "title": "Register Your Rental Agreement",
            "tip": "A registered rental agreement proves address stability and can add +20 points to your profile.",
            "impact": "Medium",
            "timeframe": "1 month",
        })

    if app_type == "SME":
        if not app_data.get("hasGSTReturns"):
            tips.append({
                "icon": "📊",
                "title": "File GST Returns Regularly",
                "tip": "Filing GST returns monthly/quarterly is a major trust signal for SME lending and can add +50 to +80 points.",
                "impact": "Very High",
                "timeframe": "3 months",
            })
        if not app_data.get("hasBusinessWebsite"):
            tips.append({
                "icon": "🌐",
                "title": "Create a Business Website",
                "tip": "A simple business website adds legitimacy and digital presence, contributing +10 to +15 points.",
                "impact": "Low",
                "timeframe": "2 weeks",
            })

    # Always-shown general tip
    tips.append({
        "icon": "📈",
        "title": "Build Data History Over Time",
        "tip": "Consistently providing more data points each month builds a stronger credit profile. Track your score every 3 months.",
        "impact": "Medium",
        "timeframe": "Ongoing",
    })

    return tips[:5]


# ────────────────────────────────────────────────────────────
# RULE-BASED SCORING ENGINE
# ────────────────────────────────────────────────────────────

def _rule_based_score(app_data: dict, app_type: str) -> dict:
    """
    Deterministic scoring from actual submitted data.
    Each section maps to a credit factor with explicit weights.
    """
    score = 500  # Base score

    # ── 1. Payment History (35% weight) ──────────────────────
    payment_score = 60
    if app_data.get("hasUtilityBills"):
        score += 50; payment_score += 15
    if app_data.get("hasUPIHistory"):
        score += 40; payment_score += 12
    if app_data.get("hasRentalAgreement"):
        score += 25; payment_score += 8
    payment_score = min(payment_score, 95)

    # ── 2. Income Stability (25% weight) ─────────────────────
    income_score = 60

    if app_type == "Individual":
        income = app_data.get("monthlyIncome") or 0
        if   income >= 75_000: score += 80; income_score += 25
        elif income >= 50_000: score += 60; income_score += 18
        elif income >= 30_000: score += 35; income_score += 10
        elif income >= 15_000: score += 15; income_score +=  5

        emp = (app_data.get("employmentType") or "").lower()
        if   emp == "salaried":                        score += 45; income_score += 10
        elif emp in ("self-employed", "business"):     score += 25; income_score +=  6
        elif emp == "freelancer":                      score += 10; income_score +=  3

        years_emp = app_data.get("yearsEmployed") or 0
        if   years_emp >= 5: score += 30; income_score += 8
        elif years_emp >= 2: score += 15; income_score += 4

        qual = (app_data.get("qualification") or "").lower()
        if   qual in ("postgraduate", "professional"): score += 20
        elif qual == "graduate":                        score += 12
        elif qual == "diploma":                         score +=  6

    else:  # SME
        revenue = app_data.get("annualRevenue") or 0
        if   revenue >= 5_000_000: score += 80; income_score += 25
        elif revenue >= 2_000_000: score += 55; income_score += 18
        elif revenue >=   500_000: score += 30; income_score += 10
        elif revenue >=   100_000: score += 10; income_score +=  4

        profit      = app_data.get("averageMonthlyProfit") or 0
        monthly_rev = max(app_data.get("monthlyRevenue") or 1, 1)
        pm = profit / monthly_rev
        if   pm >= 0.20: score += 25; income_score += 8
        elif pm >= 0.10: score += 12; income_score += 4

        if app_data.get("hasGSTReturns"): score += 50; income_score += 10
        if app_data.get("hasITReturns"):  score += 25; income_score +=  5

        vintage = datetime.now().year - (app_data.get("yearOfEstablishment") or datetime.now().year)
        if   vintage >= 5: score += 40; income_score += 10
        elif vintage >= 2: score += 20; income_score +=  5

    income_score = min(income_score, 95)

    # ── 3. Alternative Data (20% weight) ─────────────────────
    alt_score = 65
    if app_data.get("hasBankAccount"):
        score += 20; alt_score += 10
        bal = app_data.get("averageBalance") or 0
        if   bal >= 100_000: score += 30; alt_score += 12
        elif bal >=  30_000: score += 15; alt_score +=  6

    if app_data.get("hasSocialMedia") or app_data.get("hasDigitalPresence"):
        score += 15; alt_score += 5

    if app_type == "SME":
        if app_data.get("hasBusinessWebsite"): score += 15; alt_score += 5
        tx = app_data.get("monthlyTransactions") or 0
        if tx > 100:                           score += 20; alt_score += 8

    alt_score = min(alt_score, 95)

    # ── 4. Employment / Business Profile (15% weight) ────────
    prof_score = 70
    if app_type == "SME":
        reg = (app_data.get("registrationType") or "").lower()
        if reg in ("private-limited", "public-limited", "llp"):
            score += 20; prof_score += 10
        elif reg == "partnership":
            score += 10; prof_score +=  5

        emp_count = app_data.get("numberOfEmployees") or ""
        if any(x in emp_count for x in ("100", "51")):
            score += 15; prof_score += 8
        elif any(x in emp_count for x in ("26", "11")):
            score +=  8; prof_score += 4

    prof_score = min(prof_score, 95)

    # ── 5. Debt Burden (5% weight) ───────────────────────────
    loan = app_data.get("loanAmount") or 0
    debt_score = 75
    if app_type == "Individual":
        monthly = max(app_data.get("monthlyIncome") or 1, 1)
        dti = loan / (monthly * 12)
        debt_score = 85 if dti < 2 else (70 if dti < 4 else 55)
    else:
        revenue = max(app_data.get("annualRevenue") or 1, 1)
        ltr = loan / revenue
        debt_score = 85 if ltr < 0.5 else (70 if ltr < 1.5 else 55)

    # ── Clamp final score ─────────────────────────────────────
    score = max(300, min(score, 975))

    # ── Strength / improvement narratives ────────────────────
    strengths, improvements = _build_narratives(app_data, app_type)
    recommendations = [
        "Maintain at least 12 months of consistent payment records",
        "Keep bank account balance above ₹10,000 at month-end",
        "Ensure all mobile/utility bills are paid before the due date",
    ]

    # ── Factor breakdown ──────────────────────────────────────
    prof_label = "Employment Profile" if app_type == "Individual" else "Business Profile"
    factors = [
        {"name": "Payment History",  "score": payment_score, "weight": 35,
         "description": "Utility bills, rent payments, and recurring obligations"},
        {"name": "Income Stability", "score": income_score,  "weight": 25,
         "description": "Employment consistency, revenue regularity, and income level"},
        {"name": "Alternative Data", "score": alt_score,     "weight": 20,
         "description": "Digital footprint: UPI, bank activity, and online presence"},
        {"name": prof_label,         "score": prof_score,    "weight": 15,
         "description": "Work/business history, stability, and track record"},
        {"name": "Debt Burden",      "score": debt_score,    "weight": 5,
         "description": "Loan amount relative to income or revenue capacity"},
    ]

    coach_tips = _generate_coach_tips(factors, app_data, app_type)
    category   = _get_category(score)
    cfg        = _build_score_config()[category]
    max_key    = "individual_max" if app_type == "Individual" else "sme_max"
    confidence = min(72 + (score - 300) // 15, 96)

    return {
        "creditScore":    score,
        "riskCategory":   category,
        "approvalStatus": cfg["approval"],
        "interestRate":   cfg["rate"],
        "maxLoanEligible": _fmt_inr(cfg[max_key]),
        "factors":        factors,
        "strengths":      strengths,
        "improvements":   improvements,
        "recommendations": recommendations,
        "coachTips":      coach_tips,
        "aiConfidence":   float(confidence),
        "modelUsed":      "Rule-Based Scoring Engine",
    }


def _build_narratives(app_data: dict, app_type: str) -> tuple[list, list]:
    """Return (strengths, improvements) lists from applicant data."""
    strengths, improvements = [], []

    if app_data.get("hasUtilityBills"):
        strengths.append("Regular utility bill payments on record")
    if app_data.get("hasUPIHistory"):
        strengths.append("Active digital payment trail via UPI")
    if app_data.get("hasBankAccount"):
        strengths.append("Verified bank account with transaction history")

    if app_type == "Individual":
        if (app_data.get("employmentType") or "").lower() == "salaried":
            strengths.append("Stable salaried employment — reduces income risk")
        if (app_data.get("qualification") or "").lower() in ("postgraduate", "graduate", "professional"):
            strengths.append("Higher education qualification improves profile")
    else:
        if app_data.get("hasGSTReturns"):
            strengths.append("GST-compliant business with regular filings")
        est = app_data.get("yearOfEstablishment")
        if est and (datetime.now().year - est) >= 3:
            strengths.append("Established business with proven vintage")

    if not strengths:
        strengths.append("Application submitted with multiple data points")

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

    return strengths, improvements


# ────────────────────────────────────────────────────────────
# PUBLIC API
# ────────────────────────────────────────────────────────────

def calculate_credit_score(app_data: dict, app_type: str) -> dict:
    """
    Public entry point for the scoring service.
    Routes to ML model if available; otherwise uses rule-based engine.
    Always returns the same dict shape.
    """
    ml_model = get_model()

    if settings.use_ml_model and ml_model is not None:
        try:
            # Attempt ML inference — requires feature_engineering module
            from ml.feature_engineering import extract_features  # type: ignore
            features       = extract_features(app_data, app_type)
            ml_score       = int(ml_model.predict([features])[0])
            result         = _rule_based_score(app_data, app_type)
            result["creditScore"]    = ml_score
            result["riskCategory"]   = _get_category(ml_score)
            category                 = result["riskCategory"]
            cfg                      = _build_score_config()[category]
            max_key                  = "individual_max" if app_type == "Individual" else "sme_max"
            result["approvalStatus"] = cfg["approval"]
            result["interestRate"]   = cfg["rate"]
            result["maxLoanEligible"] = _fmt_inr(cfg[max_key])
            result["modelUsed"]      = "XGBoost ML Model"
            result["aiConfidence"]   = float(min(72 + (ml_score - 300) // 15, 96))
            return result
        except Exception as exc:
            logger.warning(f"ML inference failed, falling back to rule-based: {exc}")

    return _rule_based_score(app_data, app_type)
