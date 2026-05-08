"""
Crededge — Database Layer
SQLAlchemy engine, session factory, and declarative base.
All models import Base from here.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def add_missing_columns() -> None:
    """
    Add new engine columns to existing tables without dropping data.
    Safe to call multiple times (checks before ALTER TABLE).
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    try:
        existing = {c["name"] for c in inspector.get_columns("applications")}
    except Exception:
        return  # Table doesn't exist yet, create_tables will handle it

    new_cols = {
        "fraud_risk": "VARCHAR DEFAULT 'Low'",
        "fraud_flags_json": "TEXT",
        "fraud_score": "INTEGER DEFAULT 100",
        "psychometric_score": "INTEGER",
        "psychometric_bonus": "INTEGER DEFAULT 0",
        "psychometric_completed": "INTEGER DEFAULT 0",
        "psychometric_breakdown_json": "TEXT",
        "shap_waterfall_json": "TEXT",
        "peer_percentile": "REAL",
        "peer_avg_score": "INTEGER",
        "peer_count": "INTEGER",
        "peer_group_label": "VARCHAR",
        "bank_statement_uploaded": "INTEGER DEFAULT 0",
        "bank_statement_score": "INTEGER",
        "bank_statement_bonus": "INTEGER DEFAULT 0",
        "bank_cash_flow_json": "TEXT",
        "ocr_docs_verified": "INTEGER DEFAULT 0",
        "ocr_bonus": "INTEGER DEFAULT 0",
        "ocr_verified_list_json": "TEXT",
        "aa_consent_created": "INTEGER DEFAULT 0",
        "aa_verified": "INTEGER DEFAULT 0",
        "aa_bonus": "INTEGER DEFAULT 0",
        "aa_verified_income": "REAL",
        "engine_contributions_json": "TEXT",
    }

    with engine.connect() as conn:
        for col, col_type in new_cols.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col} {col_type}"))
        conn.commit()


def create_tables() -> None:
    """Create all tables and migrate existing ones. Called once at startup from main.py."""
    import models.application  # noqa: F401
    add_missing_columns()           # Migrate existing DB first
    Base.metadata.create_all(bind=engine)
