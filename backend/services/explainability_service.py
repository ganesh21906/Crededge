"""
Engine 3 — Explainability Service (SHAP-style Waterfall)
Generates a human-readable factor contribution breakdown.
Each factor shows: how many points it added/removed and a plain-language explanation.
"""


def generate_waterfall(app_data: dict, app_type: str, base_score: int, final_score: int) -> list:
    """
    Reverse-engineer the rule-based scoring to produce a plain-language waterfall.
    Each entry: {factor, contribution, direction, explanation, category}
    Sorted by |contribution| descending.
    """
    waterfall = []
    baseline = 500  # Same as rule-based engine base

    # ── Payment History factors ───────────────────────────────
    if app_data.get("hasUtilityBills"):
        waterfall.append({
            "factor": "Utility Bills Payment History",
            "contribution": 50,
            "direction": "positive",
            "explanation": "Consistent utility bill payments demonstrate financial discipline",
            "category": "Payment History",
        })
    else:
        waterfall.append({
            "factor": "Utility Bills Missing",
            "contribution": -35,
            "direction": "negative",
            "explanation": "No utility bill records reduce payment history evidence",
            "category": "Payment History",
        })

    if app_data.get("hasUPIHistory"):
        waterfall.append({
            "factor": "Active UPI Transaction History",
            "contribution": 40,
            "direction": "positive",
            "explanation": "Regular UPI usage (10+ monthly) shows active financial engagement",
            "category": "Payment History",
        })
    else:
        waterfall.append({
            "factor": "No UPI Activity",
            "contribution": -25,
            "direction": "negative",
            "explanation": "No digital payment trail reduces alternative credit evidence",
            "category": "Payment History",
        })

    if app_data.get("hasRentalAgreement"):
        waterfall.append({
            "factor": "Registered Rental Agreement",
            "contribution": 25,
            "direction": "positive",
            "explanation": "Rental agreement proves address stability and monthly commitment pattern",
            "category": "Payment History",
        })

    # ── Income factors ────────────────────────────────────────
    if app_type == "Individual":
        income = app_data.get("monthlyIncome") or 0
        if income >= 75_000:
            waterfall.append({"factor": "High Monthly Income (₹75k+)", "contribution": 80,
                "direction": "positive", "explanation": "Income above ₹75,000/month significantly reduces default risk",
                "category": "Income Stability"})
        elif income >= 50_000:
            waterfall.append({"factor": "Above-Average Income (₹50k-75k)", "contribution": 60,
                "direction": "positive", "explanation": "Income of ₹50,000+ per month provides strong repayment capacity",
                "category": "Income Stability"})
        elif income >= 30_000:
            waterfall.append({"factor": "Moderate Income (₹30k-50k)", "contribution": 35,
                "direction": "positive", "explanation": "Income of ₹30,000+ shows basic repayment viability",
                "category": "Income Stability"})
        elif income >= 15_000:
            waterfall.append({"factor": "Lower Income (₹15k-30k)", "contribution": 15,
                "direction": "positive", "explanation": "Minimum income threshold — higher loan amounts may be restricted",
                "category": "Income Stability"})
        else:
            waterfall.append({"factor": "Very Low Income (<₹15k)", "contribution": -30,
                "direction": "negative", "explanation": "Income below ₹15,000 significantly limits loan eligibility",
                "category": "Income Stability"})

        emp = (app_data.get("employmentType") or "").lower()
        if emp == "salaried":
            waterfall.append({"factor": "Salaried Employment", "contribution": 45,
                "direction": "positive", "explanation": "Fixed salary from employer is the most predictable income source",
                "category": "Income Stability"})
        elif emp in ("self-employed", "business"):
            waterfall.append({"factor": "Self-Employed / Business Owner", "contribution": 25,
                "direction": "positive", "explanation": "Business income shows entrepreneurial initiative — slightly higher variance",
                "category": "Income Stability"})
        elif emp == "freelancer":
            waterfall.append({"factor": "Freelancer Income", "contribution": 10,
                "direction": "positive", "explanation": "Freelance income is variable — additional stability signals needed",
                "category": "Income Stability"})

        years_emp = app_data.get("yearsEmployed") or 0
        if years_emp >= 5:
            waterfall.append({"factor": "5+ Years Employment Tenure", "contribution": 30,
                "direction": "positive", "explanation": "Long employment tenure strongly predicts future income stability",
                "category": "Income Stability"})
        elif years_emp >= 2:
            waterfall.append({"factor": "2-5 Years Employment Tenure", "contribution": 15,
                "direction": "positive", "explanation": "2+ years at same employer indicates stable career trajectory",
                "category": "Income Stability"})
        elif years_emp < 1:
            waterfall.append({"factor": "New Employee (<1 Year)", "contribution": -10,
                "direction": "negative", "explanation": "Employment less than 1 year increases income stability risk",
                "category": "Income Stability"})

    else:  # SME
        revenue = app_data.get("annualRevenue") or 0
        if revenue >= 5_000_000:
            waterfall.append({"factor": "High Annual Revenue (₹50L+)", "contribution": 80,
                "direction": "positive", "explanation": "Revenue above ₹50 lakhs places business in strong SME category",
                "category": "Income Stability"})
        elif revenue >= 2_000_000:
            waterfall.append({"factor": "Good Annual Revenue (₹20L-50L)", "contribution": 55,
                "direction": "positive", "explanation": "Revenue between ₹20-50 lakhs demonstrates established business",
                "category": "Income Stability"})
        elif revenue >= 500_000:
            waterfall.append({"factor": "Moderate Annual Revenue (₹5L-20L)", "contribution": 30,
                "direction": "positive", "explanation": "Revenue in ₹5-20 lakh range shows active business operations",
                "category": "Income Stability"})
        else:
            waterfall.append({"factor": "Low Annual Revenue (<₹5L)", "contribution": -10,
                "direction": "negative", "explanation": "Revenue below ₹5 lakhs limits loan capacity significantly",
                "category": "Income Stability"})

        if app_data.get("hasGSTReturns"):
            waterfall.append({"factor": "GST Returns Filed Regularly", "contribution": 50,
                "direction": "positive", "explanation": "Regular GST filing is the strongest proof of legitimate business activity",
                "category": "Income Stability"})
        else:
            waterfall.append({"factor": "No GST Returns", "contribution": -25,
                "direction": "negative", "explanation": "Absence of GST filings reduces business compliance score significantly",
                "category": "Income Stability"})

    # ── Alternative Data ──────────────────────────────────────
    if app_data.get("hasBankAccount"):
        waterfall.append({"factor": "Active Bank Account", "contribution": 20,
            "direction": "positive", "explanation": "Formal bank account enables transaction history verification",
            "category": "Alternative Data"})
        bal = app_data.get("averageBalance") or 0
        if bal >= 100_000:
            waterfall.append({"factor": "High Bank Balance (₹1L+)", "contribution": 30,
                "direction": "positive", "explanation": "Maintaining ₹1 lakh+ average balance shows financial buffer",
                "category": "Alternative Data"})
        elif bal >= 30_000:
            waterfall.append({"factor": "Moderate Bank Balance (₹30k-1L)", "contribution": 15,
                "direction": "positive", "explanation": "Consistent balance above ₹30,000 demonstrates saving discipline",
                "category": "Alternative Data"})
        elif bal > 0:
            waterfall.append({"factor": "Low Bank Balance (<₹30k)", "contribution": 5,
                "direction": "positive", "explanation": "Bank presence is positive but higher balance needed for better score",
                "category": "Alternative Data"})
    else:
        waterfall.append({"factor": "No Bank Account", "contribution": -30,
            "direction": "negative", "explanation": "Without a bank account, income and payment verification is very limited",
            "category": "Alternative Data"})

    if app_data.get("hasSocialMedia") or app_data.get("hasDigitalPresence"):
        waterfall.append({"factor": "Digital / Social Media Presence", "contribution": 15,
            "direction": "positive", "explanation": "Online presence adds legitimacy and provides identity verification signals",
            "category": "Alternative Data"})

    # ── Debt burden ───────────────────────────────────────────
    loan = app_data.get("loanAmount") or 0
    income_ref = (app_data.get("monthlyIncome") or 1) * 12 if app_type == "Individual" else (app_data.get("annualRevenue") or 1)
    ratio = loan / income_ref if income_ref else 0
    if ratio < 2:
        waterfall.append({"factor": "Conservative Loan-to-Income Ratio", "contribution": 15,
            "direction": "positive", "explanation": f"Loan amount is {ratio:.1f}x annual income — well within safe range",
            "category": "Debt Burden"})
    elif ratio > 5:
        waterfall.append({"factor": "High Loan-to-Income Ratio", "contribution": -20,
            "direction": "negative", "explanation": f"Loan amount is {ratio:.1f}x annual income — above recommended 4x maximum",
            "category": "Debt Burden"})

    # Sort by absolute contribution
    waterfall.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    # Trim to top 10 most impactful
    return waterfall[:10]
