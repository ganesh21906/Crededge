"""
Crededge — Shared FastAPI Dependencies
Injected via Depends() in route handlers.
Keeps route functions clean of infrastructure concerns.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database import SessionLocal
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")


# ── Database session ─────────────────────────────────────────

def get_db() -> Session:
    """Yield a database session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Admin auth ───────────────────────────────────────────────

def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    """
    Validate JWT token and return the admin username.
    Raises 401 if token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username != settings.admin_username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
