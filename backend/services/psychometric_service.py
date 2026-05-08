"""
Engine 2 — Psychometric Scoring Service
15-question behavioral + financial IQ assessment.
Produces psychometric_score (0-100) and score bonus (0-60 pts).
"""

from typing import List, Optional

QUESTIONS = [
    # ── Financial IQ (5 questions) ───────────────────────────
    {
        "id": "fin_01", "category": "Financial IQ", "icon": "🧮",
        "text": "If you borrow ₹50,000 at 12% annual interest for 1 year, how much do you repay in total?",
        "options": ["₹50,600", "₹56,000", "₹51,200", "₹50,120"],
        "scoring": [0, 10, 0, 0],
        "explanation": "12% of ₹50,000 = ₹6,000 interest → total ₹56,000",
    },
    {
        "id": "fin_02", "category": "Financial IQ", "icon": "🧮",
        "text": "What happens if you miss an EMI payment on a loan?",
        "options": [
            "Penalty charges + negative credit impact",
            "The missed EMI is added to next month",
            "The bank resets your loan tenure",
            "Nothing if it's your first miss",
        ],
        "scoring": [10, 0, 0, 0],
        "explanation": "Missing EMI triggers penalty fees and harms credit score",
    },
    {
        "id": "fin_03", "category": "Financial IQ", "icon": "🧮",
        "text": "₹10,000 at 6% compounded annually. After 2 years you have approximately:",
        "options": ["₹11,200", "₹11,236", "₹10,600", "₹12,000"],
        "scoring": [2, 10, 0, 0],
        "explanation": "10000 × 1.06² = ₹11,236",
    },
    {
        "id": "fin_04", "category": "Financial IQ", "icon": "🧮",
        "text": "What is considered a healthy debt-to-income ratio?",
        "options": ["Less than 40%", "Less than 80%", "More than 60%", "Exactly 50%"],
        "scoring": [10, 2, 0, 0],
        "explanation": "Financial advisors recommend keeping total EMI below 40% of income",
    },
    {
        "id": "fin_05", "category": "Financial IQ", "icon": "🧮",
        "text": "Monthly income ₹30,000. What is the safe maximum monthly EMI?",
        "options": ["₹25,000", "₹15,000", "₹12,000", "₹5,000"],
        "scoring": [0, 5, 10, 3],
        "explanation": "40% rule: 40% of ₹30,000 = ₹12,000 max EMI",
    },
    # ── Future Orientation (4 questions) ─────────────────────
    {
        "id": "fut_01", "category": "Future Orientation", "icon": "🔮",
        "text": "You unexpectedly receive ₹10,000. What do you do?",
        "options": [
            "Save most, spend a little",
            "Spend it on something you want",
            "Invest in business or stocks",
            "Give to family members",
        ],
        "scoring": [10, 2, 8, 5],
        "explanation": "Saving and investing reflect future-oriented financial behavior",
    },
    {
        "id": "fut_02", "category": "Future Orientation", "icon": "🔮",
        "text": "Would you prefer ₹1,000 today or ₹1,400 in 6 months?",
        "options": ["₹1,000 today", "₹1,400 in 6 months"],
        "scoring": [2, 10],
        "explanation": "₹1,400 in 6 months is a 40% return — patience signals creditworthiness",
        "consistency_id": "fut_02",  # Used for consistency check
    },
    {
        "id": "fut_03", "category": "Future Orientation", "icon": "🔮",
        "text": "How far ahead do you plan your finances?",
        "options": [
            "Month by month", "3-6 months ahead",
            "1-2 year financial plan", "5+ year financial plan",
        ],
        "scoring": [2, 5, 8, 10],
        "explanation": "Long-term financial planning strongly predicts loan repayment",
    },
    {
        "id": "fut_04", "category": "Future Orientation", "icon": "🔮",
        "text": "You earn ₹50,000 profit from a good business month. What do you do first?",
        "options": [
            "Pay off existing debts first",
            "Reinvest in the business",
            "Distribute as salary to yourself",
            "Keep it all as emergency savings",
        ],
        "scoring": [9, 10, 3, 7],
        "explanation": "Debt repayment and reinvestment show financial responsibility",
    },
    # ── Risk Attitude (3 questions) ──────────────────────────
    {
        "id": "risk_01", "category": "Risk Attitude", "icon": "⚖️",
        "text": "A business idea promises 30% returns but 40% chance of failure. Would you invest?",
        "options": [
            "Only if I can afford to lose the amount",
            "Absolutely — great returns",
            "No, I prefer safer options",
            "Invest half, keep half safe",
        ],
        "scoring": [8, 2, 6, 10],
        "explanation": "Balanced risk attitude (not too cautious, not reckless) is optimal",
    },
    {
        "id": "risk_02", "category": "Risk Attitude", "icon": "⚖️",
        "text": "Do you have any form of insurance (health, life, or business)?",
        "options": [
            "Yes, multiple policies", "Yes, at least one policy",
            "No, but planning to", "No, don't believe in it",
        ],
        "scoring": [10, 7, 4, 0],
        "explanation": "Insurance ownership shows risk management awareness",
    },
    {
        "id": "risk_03", "category": "Risk Attitude", "icon": "⚖️",
        "text": "Your income drops 30% for a month due to slow season. What do you do?",
        "options": [
            "Use emergency savings",
            "Take a loan immediately",
            "Cut non-essential expenses",
            "Borrow from friends/family",
        ],
        "scoring": [10, 3, 8, 5],
        "explanation": "Using savings and cutting expenses shows financial maturity",
    },
    # ── Integrity (3 questions) ──────────────────────────────
    {
        "id": "int_01", "category": "Integrity", "icon": "🤝",
        "text": "If you can't repay a loan EMI on time, what do you do?",
        "options": [
            "Contact the lender immediately and explain",
            "Wait to see if lender notices",
            "Ignore it and pay when possible",
            "Avoid all contact",
        ],
        "scoring": [10, 2, 1, 0],
        "explanation": "Proactive communication with lenders is crucial for trust",
    },
    {
        "id": "int_02", "category": "Integrity", "icon": "🤝",
        "text": "A friend owes you ₹5,000 for 3 months. What do you do?",
        "options": [
            "Politely remind and follow up",
            "Wait patiently without reminding",
            "Forget it to avoid conflict",
            "Demand immediate repayment",
        ],
        "scoring": [10, 6, 2, 4],
        "explanation": "Following up on debts signals you take financial commitments seriously",
    },
    {
        "id": "int_03", "category": "Integrity", "icon": "🤝",
        # Consistency check — similar to fut_02 (₹1,000 today vs ₹1,400 in 6 months)
        "text": "Would you choose ₹900 now or wait 6 months for ₹1,350?",
        "options": ["₹900 now", "₹1,350 in 6 months"],
        "scoring": [2, 10],
        "explanation": "Consistency check — should align with earlier patience question",
        "consistency_check": "fut_02",  # Maps answer 0→0 / 1→1 for consistency
    },
]


def get_questions() -> List[dict]:
    """Return questions without scoring metadata (safe to send to frontend)."""
    return [
        {
            "id": q["id"],
            "category": q["category"],
            "icon": q["icon"],
            "text": q["text"],
            "options": q["options"],
            "explanation": q.get("explanation", ""),
        }
        for q in QUESTIONS
    ]


def score_responses(responses: dict) -> dict:
    """
    responses: {question_id: answer_index}
    Returns detailed psychometric result.
    """
    q_map = {q["id"]: q for q in QUESTIONS}

    category_scores = {
        "Financial IQ": {"total": 0, "max": 0},
        "Future Orientation": {"total": 0, "max": 0},
        "Risk Attitude": {"total": 0, "max": 0},
        "Integrity": {"total": 0, "max": 0},
    }
    consistency_bonus = 0

    for q_id, answer_idx in responses.items():
        q = q_map.get(q_id)
        if not q:
            continue
        scoring = q.get("scoring", [])
        if answer_idx < len(scoring):
            pts = scoring[answer_idx]
        else:
            pts = 0

        cat = q.get("category", "Integrity")
        if cat in category_scores:
            category_scores[cat]["total"] += pts
            category_scores[cat]["max"] += max(q.get("scoring", [10]))

    # Consistency check
    fut_02 = responses.get("fut_02")
    int_03 = responses.get("int_03")
    if fut_02 is not None and int_03 is not None:
        if fut_02 == int_03:
            consistency_bonus = 10

    # Normalize each category to 0-100
    def pct(cat_data):
        if cat_data["max"] == 0:
            return 0
        return round(cat_data["total"] / cat_data["max"] * 100)

    fin_iq       = pct(category_scores["Financial IQ"])
    future_ori   = pct(category_scores["Future Orientation"])
    risk_att     = pct(category_scores["Risk Attitude"])
    integrity    = pct(category_scores["Integrity"])

    # Weighted overall score
    overall = int(
        fin_iq * 0.35 +
        future_ori * 0.30 +
        risk_att * 0.20 +
        integrity * 0.15 +
        consistency_bonus
    )
    overall = min(overall, 100)

    # Score bonus: max +60 points on credit score
    bonus = int(overall * 0.60)

    return {
        "psychometricScore": overall,
        "psychometricBonus": bonus,
        "breakdown": {
            "financialIQ":       fin_iq,
            "futureOrientation": future_ori,
            "riskAttitude":      risk_att,
            "integrity":         integrity,
            "consistencyBonus":  consistency_bonus,
        },
        "interpretation": _interpret(overall),
    }


def _interpret(score: int) -> str:
    if score >= 85:
        return "Excellent financial mindset — strong predictor of loan repayment"
    if score >= 70:
        return "Good financial awareness with strong repayment intent"
    if score >= 55:
        return "Moderate financial literacy — improving knowledge will boost eligibility"
    return "Basic financial awareness — consider credit counseling before applying"
