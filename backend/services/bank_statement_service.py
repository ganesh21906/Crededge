"""
Engine 5 — Bank Statement Cash Flow Analyzer
Parses uploaded PDF bank statements to extract cash flow signals.
Falls back gracefully if pdfplumber is not installed.
"""

import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def analyze_bank_statement(file_bytes: bytes, filename: str) -> dict:
    """
    Parse a bank statement PDF and extract credit scoring signals.
    Returns a score (0-100) and bonus points (0-120).
    Gracefully handles missing libraries or parse failures.
    """
    try:
        import pdfplumber
        return _parse_with_pdfplumber(file_bytes)
    except ImportError:
        logger.warning("pdfplumber not installed — using heuristic analysis")
        return _heuristic_analysis(file_bytes, filename)
    except Exception as e:
        logger.warning(f"Bank statement parse failed: {e}")
        return _error_result(str(e))


def _parse_with_pdfplumber(file_bytes: bytes) -> dict:
    """Full PDF parsing with pdfplumber."""
    import pdfplumber
    import pandas as pd

    credits, debits, balances = [], [], []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            lines = page.extract_text() or ""
            for line in lines.split("\n"):
                credit = _extract_amount(line, ["CR", "credit", "salary", "NEFT", "IMPS"])
                debit  = _extract_amount(line, ["DR", "debit", "withdrawal"])
                bal    = _extract_balance(line)
                if credit: credits.append(credit)
                if debit:  debits.append(debit)
                if bal:    balances.append(bal)

    return _score_cash_flow(credits, debits, balances)


def _heuristic_analysis(file_bytes: bytes, filename: str) -> dict:
    """
    Simple keyword-based analysis when pdfplumber is unavailable.
    Still provides useful signals from raw text extraction.
    """
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text = ""

    signals = {
        "hasSalaryKeyword":   bool(re.search(r"salary|SALARY|payroll", text, re.IGNORECASE)),
        "hasUPIKeyword":      bool(re.search(r"UPI|PhonePe|GPay|Paytm", text, re.IGNORECASE)),
        "hasEMIKeyword":      bool(re.search(r"EMI|loan|lending", text, re.IGNORECASE)),
        "hasNEFTKeyword":     bool(re.search(r"NEFT|RTGS|IMPS", text, re.IGNORECASE)),
        "hasDishonorKeyword": bool(re.search(r"dishonour|dishonor|bounced|returned", text, re.IGNORECASE)),
        "pageCount":          text.count("Page"),
    }

    score = 60
    if signals["hasSalaryKeyword"]: score += 15
    if signals["hasUPIKeyword"]:    score += 10
    if signals["hasNEFTKeyword"]:   score += 8
    if signals["hasDishonorKeyword"]: score -= 20
    score = max(0, min(100, score))

    return {
        "bankStatementScore": score,
        "bankStatementBonus": int(score * 0.8),
        "cashFlow": {
            "method":          "Heuristic (PDF text analysis)",
            "salaryDetected":  signals["hasSalaryKeyword"],
            "digitalPayments": signals["hasUPIKeyword"],
            "dishonorFound":   signals["hasDishonorKeyword"],
        },
        "parsed": True,
        "warning": "Install pdfplumber for detailed transaction-level analysis",
    }


def _score_cash_flow(credits: list, debits: list, balances: list) -> dict:
    """Compute cash flow score from extracted transactions."""
    if not credits:
        return _error_result("No credit transactions found in statement")

    total_credit  = sum(credits)
    total_debit   = sum(abs(d) for d in debits)
    avg_balance   = sum(balances) / len(balances) if balances else 0
    savings_rate  = 1 - (total_debit / total_credit) if total_credit > 0 else 0
    income_regular = len(credits) >= 6  # At least 6 monthly credits

    score = 60
    if income_regular:   score += 15
    if savings_rate > 0.2: score += 15
    elif savings_rate > 0.1: score += 8
    if avg_balance > 50_000: score += 10
    elif avg_balance > 15_000: score += 5
    score = min(100, score)

    return {
        "bankStatementScore": score,
        "bankStatementBonus": int(score * 1.2),  # Max 120 bonus points
        "cashFlow": {
            "method":         "Full PDF Parse (pdfplumber)",
            "totalCredits":   round(total_credit, 2),
            "totalDebits":    round(total_debit, 2),
            "avgBalance":     round(avg_balance, 2),
            "savingsRate":    round(savings_rate * 100, 1),
            "regularIncome":  income_regular,
            "creditCount":    len(credits),
        },
        "parsed": True,
    }


def _extract_amount(line: str, keywords: list) -> Optional[float]:
    for kw in keywords:
        if kw.lower() in line.lower():
            amounts = re.findall(r"[\d,]+\.\d{2}", line)
            if amounts:
                return float(amounts[-1].replace(",", ""))
    return None


def _extract_balance(line: str) -> Optional[float]:
    if re.search(r"balance|BAL|closing", line, re.IGNORECASE):
        amounts = re.findall(r"[\d,]+\.\d{2}", line)
        if amounts:
            return float(amounts[-1].replace(",", ""))
    return None


def _error_result(reason: str) -> dict:
    return {
        "bankStatementScore": 0,
        "bankStatementBonus": 0,
        "cashFlow": {"method": "Failed", "error": reason},
        "parsed": False,
    }
