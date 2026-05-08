"""
Crededge — ML Model Loader
Handles optional XGBoost model loading at startup.
Isolates all ML infrastructure from the scoring logic.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_model = None  # module-level singleton


def load_model() -> Optional[object]:
    """
    Attempt to load the trained XGBoost model.
    Returns the model if successful, None otherwise.
    Called once at application startup.
    """
    global _model
    try:
        import joblib
        model_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "data", "credit_risk_xgboost_v1.pkl"
        )
        model_path = os.path.abspath(model_path)
        if not os.path.exists(model_path):
            logger.info(f"ML model not found at {model_path} — using rule-based engine")
            return None
        _model = joblib.load(model_path)
        logger.info("✅ XGBoost ML model loaded successfully")
        return _model
    except ImportError:
        logger.warning("joblib not installed — ML model unavailable")
    except Exception as e:
        logger.warning(f"ML model load failed ({e}) — falling back to rule-based engine")
    return None


def get_model() -> Optional[object]:
    """Return the loaded model singleton (None if not loaded)."""
    return _model
