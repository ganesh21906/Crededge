"""
Engine 7 — Account Aggregator (AA) Service
RBI-approved consent-based bank data fetching.
This implementation provides a realistic mock flow for demonstration.
Replace with real Finvu/Setu/OneMoney API credentials for production.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory consent store (replace with DB in production)
_consent_store: dict = {}


def create_consent_request(application_id: str, user_phone: str) -> dict:
    """
    Initiate an AA consent request.
    Returns consent_handle and redirect URL for user to approve.
    In production: calls Finvu/Setu AA API.
    """
    consent_handle = f"CC-{uuid.uuid4().hex[:12].upper()}"
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    # Store consent
    _consent_store[consent_handle] = {
        "applicationId": application_id,
        "phone":        user_phone,
        "status":       "PENDING",
        "createdAt":    datetime.utcnow().isoformat(),
        "expiresAt":    expires_at.isoformat(),
    }

    # In production, this URL would come from Finvu/Setu API
    # redirect_url = f"https://webview.finvu.in/consent/{consent_handle}"
    demo_redirect = f"http://localhost:3000/aa-consent?handle={consent_handle}&phone={user_phone}"

    logger.info(f"AA consent created: {consent_handle} for app {application_id}")

    return {
        "consentHandle": consent_handle,
        "redirectUrl":   demo_redirect,
        "expiresAt":     expires_at.isoformat(),
        "status":        "PENDING",
        "message":       "Redirect user to approve consent on their AA app",
        "provider":      "Crededge Demo AA (Setu/Finvu in production)",
    }


def simulate_consent_approval(consent_handle: str) -> dict:
    """
    Simulate the user approving consent on the AA app.
    In production: this happens via webhook callback from the AA provider.
    """
    consent = _consent_store.get(consent_handle)
    if not consent:
        return {"success": False, "error": "Consent handle not found"}

    consent["status"] = "APPROVED"
    consent["approvedAt"] = datetime.utcnow().isoformat()

    # Simulate fetching bank data after approval
    return fetch_fi_data(consent_handle)


def fetch_fi_data(consent_handle: str) -> dict:
    """
    Fetch Financial Information (FI) data after consent approval.
    Mock implementation returns realistic demo data.
    In production: calls AA provider's FI fetch API.
    """
    consent = _consent_store.get(consent_handle)
    if not consent or consent.get("status") != "APPROVED":
        return {"success": False, "error": "Consent not approved"}

    # Simulated financial data (would come from real bank via AA in production)
    mock_fi_data = {
        "accountType":   "SAVINGS",
        "bank":          "State Bank of India",
        "accountMasked": "XXXX1234",
        "period":        "Jan 2024 – Dec 2024",
        "summary": {
            "totalCredits":     312_500.00,
            "totalDebits":      248_000.00,
            "avgMonthlyCredit": 26_042.00,
            "avgBalance":       42_300.00,
            "monthsAnalyzed":   12,
            "salaryCredits":    11,
            "dishonorCount":    0,
            "savingsRate":      20.6,
        },
    }

    # Compute AA bonus
    summary    = mock_fi_data["summary"]
    aa_bonus   = 0
    verified_income = summary["avgMonthlyCredit"]

    if summary["monthsAnalyzed"] >= 6:      aa_bonus += 40
    if summary["salaryCredits"] >= 6:        aa_bonus += 30
    if summary["dishonorCount"] == 0:        aa_bonus += 20
    if summary["savingsRate"] >= 15:         aa_bonus += 10
    if summary["avgBalance"] >= 20_000:      aa_bonus += 10
    aa_bonus = min(aa_bonus, 100)

    return {
        "success":        True,
        "consentHandle":  consent_handle,
        "fiData":         mock_fi_data,
        "aaBonus":        aa_bonus,
        "aaVerifiedIncome": verified_income,
        "provider":       "SBI via Finvu AA (simulated)",
        "note":           "Real AA integration requires Finvu/Setu API keys + RBI compliance",
    }


def get_aa_status(consent_handle: str) -> dict:
    """Check current status of an AA consent request."""
    consent = _consent_store.get(consent_handle)
    if not consent:
        return {"status": "NOT_FOUND"}
    return {"status": consent.get("status"), **consent}
