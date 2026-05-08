"""
Engine 6 — OCR Document Intelligence Service
Verify utility bills, ITR, MSME certificates, GST returns via OCR.
Uses pytesseract + pdf2image; graceful fallback to filename-heuristic.
"""

import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DOCUMENT_TYPES = {
    "utility_bill":       {"label": "Utility Bill",            "bonus": 35, "signals": ["electricity", "water", "gas", "telecom"]},
    "itr":                {"label": "Income Tax Return",        "bonus": 45, "signals": ["income tax", "ITR", "assessment year", "PAN"]},
    "rent_agreement":     {"label": "Rental Agreement",         "bonus": 25, "signals": ["lease", "rent", "landlord", "tenant"]},
    "gst_return":         {"label": "GST Return",               "bonus": 50, "signals": ["GST", "GSTIN", "filing", "tax period"]},
    "msme_certificate":   {"label": "MSME Certificate",         "bonus": 40, "signals": ["MSME", "udyam", "micro enterprise", "NIC"]},
    "bank_statement":     {"label": "Bank Statement",           "bonus": 30, "signals": ["account statement", "account number", "IFSC"]},
    "salary_slip":        {"label": "Salary Slip",              "bonus": 30, "signals": ["salary", "payslip", "employer", "CTC", "gross pay"]},
}


def verify_document(file_bytes: bytes, filename: str, doc_type: str) -> dict:
    """
    Attempt OCR verification of the uploaded document.
    Returns verification result with confidence and bonus points.
    """
    doc_config = DOCUMENT_TYPES.get(doc_type)
    if not doc_config:
        return {"verified": False, "error": f"Unknown document type: {doc_type}"}

    # Try full OCR
    extracted_text = _extract_text(file_bytes, filename)

    if extracted_text:
        return _verify_with_text(extracted_text, doc_type, doc_config)
    else:
        # Fallback: filename-based heuristic
        return _verify_with_filename(filename, doc_type, doc_config)


def _extract_text(file_bytes: bytes, filename: str) -> Optional[str]:
    """Try pdfplumber → pytesseract → plain text decode."""
    # PDF files
    if filename.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                return " ".join([p.extract_text() or "" for p in pdf.pages])
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"pdfplumber OCR failed: {e}")

    # Image files
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        try:
            import pytesseract
            from PIL import Image
            img  = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(img)
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"pytesseract OCR failed: {e}")

    # Plain text decode fallback
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return None


def _verify_with_text(text: str, doc_type: str, config: dict) -> dict:
    """Check extracted text for expected document keywords."""
    text_lower = text.lower()
    signals    = config["signals"]
    matches    = [s for s in signals if s.lower() in text_lower]
    confidence = len(matches) / len(signals) if signals else 0
    verified   = confidence >= 0.4  # At least 40% of expected signals found

    # Extract specific data points based on document type
    extracted = {}
    if doc_type == "itr":
        pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
        if pan_match: extracted["panNumber"] = pan_match.group()
        year_match = re.search(r"Assessment Year[:\s]+(\d{4}-\d{2})", text, re.IGNORECASE)
        if year_match: extracted["assessmentYear"] = year_match.group(1)

    elif doc_type == "utility_bill":
        consumer_match = re.search(r"Consumer[:\s]+(.+?)(?:\n|$)", text, re.IGNORECASE)
        if consumer_match: extracted["consumerName"] = consumer_match.group(1).strip()[:50]

    elif doc_type == "gst_return":
        gstin_match = re.search(r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]", text)
        if gstin_match: extracted["gstin"] = gstin_match.group()

    return {
        "verified":    verified,
        "docType":     doc_type,
        "docLabel":    config["label"],
        "confidence":  round(confidence * 100, 1),
        "signalsFound": matches,
        "bonusPoints": config["bonus"] if verified else int(config["bonus"] * 0.3),
        "extractedData": extracted,
        "method":      "OCR Text Analysis",
    }


def _verify_with_filename(filename: str, doc_type: str, config: dict) -> dict:
    """Filename heuristic when OCR is unavailable."""
    fn_lower = filename.lower()
    expected = config["signals"]
    matches  = [s for s in expected if s.lower() in fn_lower]

    return {
        "verified":    len(matches) > 0 or doc_type in fn_lower,
        "docType":     doc_type,
        "docLabel":    config["label"],
        "confidence":  50.0,
        "signalsFound": matches,
        "bonusPoints": int(config["bonus"] * 0.5),  # Half bonus for filename-only
        "extractedData": {},
        "method":      "Filename Heuristic (install pytesseract for full OCR)",
        "warning":     "Install pytesseract + pdfplumber for full document verification",
    }


def get_supported_document_types() -> list:
    return [
        {"id": dt_id, "label": cfg["label"], "maxBonus": cfg["bonus"]}
        for dt_id, cfg in DOCUMENT_TYPES.items()
    ]
