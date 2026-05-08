"""
Engine 4 — Peer Benchmarking Service
Compares applicant against similar profiles in the database.
Provides percentile position and context message.
"""

from sqlalchemy.orm import Session
from typing import Optional


def get_peer_benchmark(app_data: dict, app_type: str, current_score: int, db: Session) -> dict:
    """
    Find similar applicants in the DB and compute benchmark metrics.
    Returns None if insufficient data (<5 peers).
    """
    from models.application import Application

    query = db.query(Application).filter(
        Application.application_type == app_type,
        Application.credit_score.isnot(None),
    )

    # Match on similar profile attributes
    if app_type == "Individual":
        emp  = (app_data.get("employmentType") or "").lower()
        state = app_data.get("state") or ""
        income = app_data.get("monthlyIncome") or 0
        income_low  = income * 0.6
        income_high = income * 1.4

        # Filter by employment type (most discriminating)
        if emp:
            import json
            all_apps = query.all()
            peers = [
                a for a in all_apps
                if json.loads(a.full_data_json or "{}").get("employmentType", "").lower() == emp
                and income_low <= (json.loads(a.full_data_json or "{}").get("monthlyIncome") or 0) <= income_high
            ]
        else:
            peers = query.all()

        label = f"{emp.title()} applicants" + (f" in {state}" if state else "")

    else:  # SME
        industry = (app_data.get("industryType") or "").lower()
        revenue  = app_data.get("annualRevenue") or 0
        rev_low  = revenue * 0.5
        rev_high = revenue * 2.0

        import json
        all_apps = query.all()
        peers = [
            a for a in all_apps
            if rev_low <= (json.loads(a.full_data_json or "{}").get("annualRevenue") or 0) <= rev_high
        ]
        label = f"{industry.title()} SMEs" if industry else "Similar SMEs"

    if len(peers) < 3:
        return {
            "available": False,
            "message": "Not enough similar applicants yet to benchmark",
        }

    scores = sorted([p.credit_score for p in peers])
    avg    = int(sum(scores) / len(scores))
    median = scores[len(scores) // 2]
    top25  = scores[int(len(scores) * 0.75)]

    # Compute percentile of current score
    below = sum(1 for s in scores if s < current_score)
    percentile = round(below / len(scores) * 100, 1)

    if percentile >= 75:
        msg = f"You scored higher than {percentile:.0f}% of {label} 🏆"
    elif percentile >= 50:
        msg = f"You're above average among {label} ({percentile:.0f}th percentile)"
    elif percentile >= 25:
        msg = f"You're slightly below average for {label} — there's room to improve"
    else:
        msg = f"Your score is in the bottom 25% of {label} — follow AI coach tips to improve"

    return {
        "available": True,
        "peerCount":     len(peers),
        "peerAvgScore":  avg,
        "peerMedian":    median,
        "peerTop25":     top25,
        "yourPercentile": percentile,
        "groupLabel":    label,
        "message":       msg,
    }
