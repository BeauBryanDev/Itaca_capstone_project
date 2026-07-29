
from __future__ import annotations
 
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
 
from app.core.logging import get_logger
from app.services.inference_service import InferenceService
from app.services.personalization_service import PersonalizationService
from app.services.recommendation_service import RecommendationService

 
logger = get_logger(__name__)
 
 

@dataclass(frozen=True)
class DiagnosticResult:
    
    """
    Complete Output of a single diagnostic run.
    """
    
    diagnostic_id: str
    maturity_level: str
    class_probabilities: dict[str, float]
    base_recommendation: str
    personalized_recommendation: str | None
    used_personalization: bool
    model_version: str
    created_at: datetime
    
    


class DiagnosticService:
    """Runs the end-to-end diagnostic flow for a client submission."""
 
    def __init__(
        self,
        inference_service: InferenceService,
        recommendation_service: RecommendationService,
        personalization_service: PersonalizationService,
        model_version: str,
    ) -> None:
        self._inference_service = inference_service
        self._recommendation_service = recommendation_service
        self._personalization_service = personalization_service
        self._model_version = model_version
 
    def run_diagnostic(
        self,
        sector: str,
        company_size: str,
        documented_processes_pct: float,
        annual_tech_budget: int,
        user_response_text: str,
        personalize: bool,
    ) -> DiagnosticResult:
        
        """Execute the full diagnostic pipeline and return the assembled result.
            """
        # inference (always runs).
        inference_result = self._inference_service.predict(
            sector=sector,
            company_size=company_size,
            documented_processes_pct=documented_processes_pct,
            annual_tech_budget=annual_tech_budget,
            user_response_text=user_response_text,
        )

        #  base recommendation from the catalog (always runs).
        base_recommendation = self._recommendation_service.get_base_recommendation(
            sector=sector,
            maturity_level=inference_result.maturity_level,
        )

        #  optional personalization. Only attempted when requested.
        # The personalization service never raises: it returns None on any
        # failure, so used_personalization is derived from whether it
        # actually produced text, not from the request flag alone.
        personalized_recommendation: str | None = None
        
        if personalize:
            
            personalized_recommendation = self._personalization_service.personalize(
                sector=sector,
                maturity_level=inference_result.maturity_level,
                base_recommendation=base_recommendation,
                user_response_text=user_response_text,
            )

        used_personalization = personalized_recommendation is not None

        result = DiagnosticResult(
            
            diagnostic_id=str(uuid.uuid4()),
            maturity_level=inference_result.maturity_level,
            class_probabilities=inference_result.class_probabilities,
            base_recommendation=base_recommendation,
            personalized_recommendation=personalized_recommendation,
            used_personalization=used_personalization,
            model_version=self._model_version,
            created_at=datetime.now(timezone.utc),
        )

        logger.info(
            "Diagnostic completed: id=%s level=%s personalized=%s",
            result.diagnostic_id,
            result.maturity_level,
            result.used_personalization,
        )
        
        return result

