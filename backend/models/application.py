"""
Crededge — Application ORM Model
Maps to the `applications` table in the database.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class Application(Base):
    __tablename__ = "applications"

    # ── Identity ─────────────────────────────────────────────
    id = Column(String, primary_key=True, index=True)
    application_type = Column(String, nullable=False)          # "Individual" | "SME"

    # ── Applicant ─────────────────────────────────────────────
    applicant_name = Column(String, nullable=False, index=True)
    email = Column(String)
    phone = Column(String)

    # ── Loan ─────────────────────────────────────────────────
    loan_amount = Column(Float)
    loan_purpose = Column(String)

    # ── Score results ─────────────────────────────────────────
    credit_score = Column(Integer)
    risk_category = Column(String)
    approval_status = Column(String)
    interest_rate = Column(String)
    max_loan_eligible = Column(String)
    ai_confidence = Column(Float)
    model_used = Column(String)

    # ── Admin review ─────────────────────────────────────────
    review_status = Column(String, default="pending")  # pending | approved | rejected
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)

    # ── Timestamps ───────────────────────────────────────────
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # ── Serialized JSON payloads ──────────────────────────────
    full_data_json = Column(Text)       # Complete form submission
    factors_json = Column(Text)         # [{name, score, weight, description}]
    strengths_json = Column(Text)       # [str, ...]
    improvements_json = Column(Text)    # [str, ...]
    recommendations_json = Column(Text) # [str, ...]
    coach_tips_json = Column(Text)      # [{icon, title, tip, impact, timeframe}]

    # ── Engine 1: Fraud Detection ─────────────────────────────
    fraud_risk = Column(String, default="Low")       # Low | Medium | High
    fraud_flags_json = Column(Text)                  # [str, ...] list of triggered flags
    fraud_score = Column(Integer, default=100)       # 0-100, lower = more suspicious

    # ── Engine 2: Psychometric ────────────────────────────────
    psychometric_score = Column(Integer, nullable=True)    # 0-100
    psychometric_bonus = Column(Integer, default=0)        # +points added to credit score
    psychometric_completed = Column(Integer, default=0)    # 0 or 1 (SQLite bool)
    psychometric_breakdown_json = Column(Text)             # {fin_iq, future_orientation, risk_attitude, integrity}

    # ── Engine 3: Explainability (SHAP-style waterfall) ───────
    shap_waterfall_json = Column(Text)               # [{factor, contribution, direction, explanation}]

    # ── Engine 4: Peer Benchmarking ───────────────────────────
    peer_percentile = Column(Float, nullable=True)   # 0-100
    peer_avg_score = Column(Integer, nullable=True)
    peer_count = Column(Integer, nullable=True)
    peer_group_label = Column(String, nullable=True) # "Salaried applicants in Maharashtra"

    # ── Engine 5: Bank Statement ──────────────────────────────
    bank_statement_uploaded = Column(Integer, default=0)  # 0 or 1
    bank_statement_score = Column(Integer, nullable=True) # 0-100
    bank_statement_bonus = Column(Integer, default=0)      # +points
    bank_cash_flow_json = Column(Text)               # {monthlyIncomeMean, savingsRate, ...}

    # ── Engine 6: OCR / Document Intelligence ─────────────────
    ocr_docs_verified = Column(Integer, default=0)   # count of verified docs
    ocr_bonus = Column(Integer, default=0)           # +points
    ocr_verified_list_json = Column(Text)            # ["utility_bill", "itr", ...]

    # ── Engine 7: Account Aggregator ──────────────────────────
    aa_consent_created = Column(Integer, default=0)  # 0 or 1
    aa_verified = Column(Integer, default=0)         # 0 or 1
    aa_bonus = Column(Integer, default=0)            # +points
    aa_verified_income = Column(Float, nullable=True)

    # ── Engine contribution summary ───────────────────────────
    engine_contributions_json = Column(Text)  # {engine_name: points_contributed}
