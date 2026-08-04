from __future__ import annotations
 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
 
from app.core.logging import get_logger
from app.models.diagnostic import Diagnostic
from app.routers.state import get_db_session, get_diagnostic_service
from app.schemas.request import DiagnosticoRequest
from app.schemas.response import DiagnosticoResponse
from app.services.diagnostico_service import DiagnosticService
from app.services.recommendation_service import RecommendationNotFoundError
 
 
logger = get_logger(__name__)

 
router = APIRouter(prefix="/diagnostico", tags=["diagnostico"])
 
 
@router.post("", response_model=DiagnosticoResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostico(
    payload: DiagnosticoRequest,
    service: DiagnosticService = Depends(get_diagnostic_service),
    db: Session = Depends(get_db_session),
) -> DiagnosticoResponse:
    """Run a new diagnostic, persist it, and return the full result.
    """
    try:
        result = service.run_diagnostic(
            sector=payload.sector.value if hasattr(payload.sector, "value") else payload.sector,
            company_size=(
                payload.company_size.value
                if hasattr(payload.company_size, "value")
                else payload.company_size
            ),
        documented_processes_pct=payload.documented_processes_pct,
        annual_tech_budget=payload.annual_tech_budget,
        user_response_text=payload.user_response_text,
        social_impact=payload.social_impact,
        personalize=payload.personalize,
    )
    except RecommendationNotFoundError as exc:
        
        logger.error("Recommendation lookup failed: %s", exc)
        
        raise HTTPException(
            
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        ) from exc
 
    # Persist the diagnostic. The stored row mirrors the result exactly.
    record = Diagnostic(
        id=result.diagnostic_id,
        company_name=payload.company_name,
        sector=payload.sector.value if hasattr(payload.sector, "value") else payload.sector,
        company_size=(
            payload.company_size.value
            if hasattr(payload.company_size, "value")
            else payload.company_size
        ),
        documented_processes_pct=payload.documented_processes_pct,
        annual_tech_budget=payload.annual_tech_budget,
        user_response_text=payload.user_response_text,
        social_impact=payload.social_impact,
        predicted_maturity_level=result.maturity_level,
        class_probabilities=result.class_probabilities,
        base_recommendation=result.base_recommendation,
        personalized_recommendation=result.personalized_recommendation,
        used_personalization=result.used_personalization,
        model_version=result.model_version,
        created_at=result.created_at,
    )
    # Persistence below inference and recommendation
    try:
        db.add(record)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            "Failed to persist diagnostic %s: %s", result.diagnostic_id, exc
        )

    return DiagnosticoResponse(
        diagnostico_id=result.diagnostic_id,
        maturity_level=result.maturity_level,
        class_probabilities=result.class_probabilities,
        base_recommendation=result.base_recommendation,
        personalized_recommendation=result.personalized_recommendation,
        used_personalization=result.used_personalization,
        model_version=result.model_version,
        created_at=result.created_at,
    )
 
 
@router.get("/{diagnostico_id}", response_model=DiagnosticoResponse)
def get_diagnostico(
    diagnostico_id: str,
    db: Session = Depends(get_db_session),
) -> DiagnosticoResponse:
    """Retrieve a previously persisted diagnostic by its identifier.
 
    Args:
        diagnostico_id: The identifier returned when the diagnostic was
            created.
        db: Database session (injected).
 
    Returns:
        The stored diagnostic, shaped as a response.
 
    Raises:
        HTTPException 404: If no diagnostic with that identifier exists.
    """
    record = db.get(Diagnostic, diagnostico_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagnostic found with id {diagnostico_id!r}.",
        )
 
    return DiagnosticoResponse(
        diagnostico_id=record.id,
        maturity_level=record.predicted_maturity_level,
        class_probabilities=record.class_probabilities,
        base_recommendation=record.base_recommendation,
        personalized_recommendation=record.personalized_recommendation,
        used_personalization=record.used_personalization,
        model_version=record.model_version,
        created_at=record.created_at,
    )
 
