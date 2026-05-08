"""
Crededge — Admin Routes (JWT protected)

GET  /api/admin/applications  — paginated list with filtering
PUT  /api/admin/applications/{id}/review  — approve / reject
GET  /api/admin/stats  — real-time statistics

All routes require a valid admin JWT (get_current_admin dependency).
"""

from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_admin
from schemas.application import ApplicationListResponse, AdminStatsResponse, AdminActionRequest
import services.application_service as svc

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/applications", response_model=ApplicationListResponse)
def list_applications(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    app_type: Optional[str] = None,
    review_status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Return paginated, filtered list of all applications. Admin only."""
    return svc.list_applications(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        app_type=app_type,
        review_status=review_status,
    )


@router.put("/applications/{application_id}/review")
def review_application(
    application_id: str,
    request: AdminActionRequest,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    """Approve or reject an application. Admin only."""
    return svc.review_application(application_id, request.action, admin_user, db)


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
):
    """Return live statistics computed from database. Public for B2B demo."""
    return svc.get_admin_stats(db)
