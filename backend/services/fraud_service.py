"""
Engine 1 — Fraud Detection & Anomaly Service
Rule-based signal analysis to flag suspicious applications.
Returns fraud_risk: "Low" | "Medium" | "High"
"""

import re
from typing import Optional
from sqlalchemy.orm import Session


def analyze_fraud(app_data: dict, app_type: str, db: Session = None) -> dict:
    """
    Runs a battery of fraud checks against the submitted application data.
    Returns a fraud result dict with risk level, flags, and score.
    """
    flags = []
    penalties = 0

    # ── 1. Income vs Lifestyle Inconsistency ─────────────────
    income = app_data.get("monthlyIncome") or app_data.get("monthlyRevenue") or 0
    loan   = app_data.get("loanAmount") or 0
    has_bank = app_data.get("hasBankAccount", False)

    if income > 150_000 and not has_bank:
        flags.append("High declared income but no bank account — inconsistent lifestyle profile")
        penalties += 25

    if income > 200_000 and not app_data.get("hasUtilityBills") and not app_data.get("hasUPIHistory"):
        flags.append("Very high income claimed but zero verifiable digital footprint")
        penalties += 20

    # ── 2. Suspiciously Round Numbers ────────────────────────
    if income > 30_000 and income % 50_000 == 0:
        flags.append(f"Declared income is a perfectly round number (₹{income:,}) — possible estimation")
        penalties += 10

    if loan > 100_000 and loan % 100_000 == 0:
        flags.append(f"Loan amount is a round figure (₹{loan:,}) — verify actual requirement")
        penalties += 5

    # ── 3. Extreme Debt-to-Income Ratio ──────────────────────
    if income > 0:
        annual_income = income * 12
        dti = loan / annual_income
        if dti > 8:
            flags.append(f"Loan-to-annual-income ratio of {dti:.1f}x is extremely high (max safe: 4x)")
            penalties += 30
        elif dti > 5:
            flags.append(f"Loan-to-annual-income ratio of {dti:.1f}x is high — additional verification needed")
            penalties += 15

    # ── 4. Field Completeness Anomaly ────────────────────────
    required_fields = ["mobileNumber", "email", "address", "pincode"]
    for f in required_fields:
        alt = app_data.get("businessName") if app_type == "SME" else None
        if not app_data.get("fullName") and not alt:
            flags.append("Applicant name missing — incomplete submission")
            penalties += 10
            break

    # ── 5. Pincode Format Validation ─────────────────────────
    pincode = str(app_data.get("pincode") or "")
    if pincode and not re.match(r"^\d{6}$", pincode):
        flags.append(f"Pincode '{pincode}' does not match 6-digit Indian format")
        penalties += 15

    # ── 6. Phone Duplication Check (if DB available) ─────────
    if db:
        from models.application import Application
        phone = app_data.get("mobileNumber") or ""
        name  = app_data.get("fullName") or app_data.get("businessName") or ""
        if phone:
            existing = db.query(Application).filter(
                Application.phone == phone
            ).first()
            if existing and existing.applicant_name.lower() != name.lower():
                flags.append(
                    f"Phone number already used by a different applicant "
                    f"('{existing.applicant_name}') — possible duplicate"
                )
                penalties += 35

    # ── 7. SME-Specific Checks ───────────────────────────────
    if app_type == "SME":
        revenue = app_data.get("annualRevenue") or 0
        monthly = app_data.get("monthlyRevenue") or 0

        if monthly > 0 and revenue > 0:
            implied_annual = monthly * 12
            discrepancy = abs(implied_annual - revenue) / max(revenue, 1)
            if discrepancy > 0.3:
                flags.append(
                    f"Annual revenue (₹{revenue:,}) is inconsistent with "
                    f"monthly revenue × 12 (₹{implied_annual:,}) — >30% discrepancy"
                )
                penalties += 20

        est_year = app_data.get("yearOfEstablishment") or 2024
        if est_year > 2025:
            flags.append("Year of establishment is in the future — data error")
            penalties += 20

        pan = app_data.get("panNumber") or ""
        if pan and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan):
            flags.append(f"PAN number format invalid: '{pan}'")
            penalties += 15

    # ── Compute fraud score (100 = clean, 0 = very suspicious) ──
    fraud_score = max(0, 100 - penalties)

    if fraud_score >= 80:
        risk = "Low"
    elif fraud_score >= 55:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "fraudRisk":   risk,
        "fraudScore":  fraud_score,
        "fraudFlags":  flags,
        "flagCount":   len(flags),
        "autoReview":  risk == "High",  # Flag for mandatory admin review
    }
