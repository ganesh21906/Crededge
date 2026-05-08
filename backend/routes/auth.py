"""
Crededge — Auth Routes
POST /api/admin/token

Thin router — delegates no business logic (auth IS the business here).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt

from config import settings
from schemas.auth import TokenResponse

router = APIRouter(prefix="/api/admin", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Issue a JWT access token for admin users.
    Uses OAuth2 password flow (username + password in form body).
    """
    if (form_data.username != settings.admin_username or
            form_data.password != settings.admin_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    token  = jwt.encode(
        {"sub": form_data.username, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return TokenResponse(access_token=token, token_type="bearer", username=form_data.username)
