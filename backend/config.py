"""
Crededge — Central Configuration
All settings read from environment / .env file.
Never import from .env directly — always use `from config import settings`.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Security ─────────────────────────────────────────────
    jwt_secret: str = "crededge-super-secret-key-CHANGE-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 hours

    # ── Admin credentials ────────────────────────────────────
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # ── Database ─────────────────────────────────────────────
    database_url: str = "sqlite:///./crededge.db"

    # ── CORS ─────────────────────────────────────────────────
    frontend_url: str = "http://localhost:3000"

    # ── ML model toggle ──────────────────────────────────────
    use_ml_model: bool = False

    # ── Score thresholds (single source of truth) ────────────
    threshold_excellent: int = 850
    threshold_good: int = 750
    threshold_fair: int = 650

    # Interest rates per risk tier
    rate_excellent: str = "10.5%"
    rate_good: str = "12.5%"
    rate_fair: str = "15.0%"
    rate_poor: str = "18.0%"

    # Max loan amounts per tier
    individual_max_excellent: int = 500_000
    individual_max_good: int = 350_000
    individual_max_fair: int = 200_000
    individual_max_poor: int = 100_000

    sme_max_excellent: int = 2_500_000
    sme_max_good: int = 1_800_000
    sme_max_fair: int = 1_200_000
    sme_max_poor: int = 800_000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — call this everywhere."""
    return Settings()


# Convenience alias for direct import
settings = get_settings()
