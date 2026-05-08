"""
Crededge — Application Routes (public)

POST /api/applications/individual
POST /api/applications/sme
GET  /api/applications/{id}

Routes are intentionally thin — all logic lives in application_service.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas.application import IndividualApplication, SMEApplication, ApplicationResponse, ApplicationSummary
import services.application_service as svc

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/individual", response_model=ApplicationResponse, status_code=201)
def submit_individual(
    application: IndividualApplication,
    db: Session = Depends(get_db),
):
    """Submit an individual loan application and receive an instant AI credit assessment."""
    return svc.create_individual_application(application, db)


@router.post("/sme", response_model=ApplicationResponse, status_code=201)
def submit_sme(
    application: SMEApplication,
    db: Session = Depends(get_db),
):
    """Submit an SME loan application and receive an instant AI credit assessment."""
    return svc.create_sme_application(application, db)


@router.get("/{application_id}", response_model=ApplicationSummary)
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
):
    """
    Public endpoint — returns application status and score details.
    Used by the 'Track Application' page.
    """
    return svc.get_application_by_id(application_id, db)
