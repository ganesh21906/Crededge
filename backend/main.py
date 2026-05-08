"""
Crededge API — Main Entry Point
================================
Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Architecture:
    main.py            ← app factory + router registration + lifecycle hooks
    config.py          ← settings (reads .env)
    database.py        ← engine + session factory
    dependencies.py    ← shared Depends() injectors
    models/            ← SQLAlchemy ORM models
    schemas/           ← Pydantic request/response schemas
    services/          ← business logic (scoring, persistence)
    ml/                ← model loading (optional XGBoost)
    routes/            ← thin HTTP handlers
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import create_tables
from ml.model_loader import load_model
from routes import auth, applications, admin, engines

# ── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifecycle hook ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("=" * 60)
    logger.info("  Crededge API v2.0 starting...")
    logger.info(f"  Database : {settings.database_url}")
    logger.info(f"  Frontend : {settings.frontend_url}")

    # Create DB tables (idempotent)
    create_tables()
    logger.info("  Database : tables ready ✅")

    # Optionally load ML model
    if settings.use_ml_model:
        model = load_model()
        if model:
            logger.info("  ML Model : XGBoost loaded ✅")
        else:
            logger.warning("  ML Model : not found — using rule-based engine ⚠️")
    else:
        logger.info("  Scoring  : rule-based engine (USE_ML_MODEL=false)")

    logger.info(f"  Docs     : http://localhost:8000/docs")
    logger.info("=" * 60)

    yield  # Application runs here

    logger.info("Crededge API shutting down...")


# ── App factory ───────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="Crededge API",
        description=(
            "AI Credit Risk Assessment for Underserved Segments.\n\n"
            "**Admin endpoints** require Bearer JWT — obtain via `POST /api/admin/token`."
        ),
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth.router)
    app.include_router(applications.router)
    app.include_router(admin.router)
    app.include_router(engines.router)

    # ── Utility endpoints ──────────────────────────────────────

    @app.get("/", tags=["system"])
    def root():
        return {
            "product": "Crededge",
            "description": "AI Credit Risk Assessment for Underserved Segments",
            "version": "2.0.0",
            "engine": "XGBoost ML" if settings.use_ml_model else "Rule-Based Scoring",
            "docs": "/docs",
        }

    @app.get("/health", tags=["system"])
    def health_check():
        from database import SessionLocal
        from datetime import datetime
        from sqlalchemy import text
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_status = "connected"
        except Exception:
            db_status = "error"
        return {
            "status": "healthy",
            "database": db_status,
            "engine": "ML" if settings.use_ml_model else "Rule-Based",
            "timestamp": datetime.utcnow().isoformat(),
        }

    return app


app = create_app()


# ── Dev server entrypoint ─────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
