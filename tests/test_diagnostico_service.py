"""Tests for app.services.diagnostico_service.DiagnosticService (the orchestrator).

The three underlying services are mocked: this module's job is to verify
orchestration (how their results are combined), not their individual
correctness, which is already covered in isolation elsewhere.
"""

from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from app.services.diagnostico_service import DiagnosticService
from app.services.inference_service import InferenceResult, InferenceService
from app.services.personalization_service import PersonalizationService
from app.services.recommendation_service import (
    RecommendationNotFoundError,
    RecommendationService,
)

CALL_KWARGS = {
    "sector": "Tecnologia",
    "company_size": "Micro",
    "documented_processes_pct": 0.1,
    "annual_tech_budget": 3_000_000,
    "user_response_text": "El trabajo es muy empirico, no hay documentacion.",
    "social_impact": None,
}


def _build_service(
    *,
    maturity_level: str = "Inicial",
    base_recommendation: str = "Mapear flujos de trabajo.",
    personalized_recommendation: str | None = None,
) -> DiagnosticService:
    inference = Mock(spec=InferenceService)
    inference.predict.return_value = InferenceResult(
        maturity_level=maturity_level,
        class_probabilities={
            "Inicial": 0.9,
            "En Desarrollo": 0.05,
            "Definido": 0.03,
            "Optimizado": 0.02,
        },
    )

    recommendation = Mock(spec=RecommendationService)
    recommendation.get_base_recommendation.return_value = base_recommendation

    personalization = Mock(spec=PersonalizationService)
    personalization.personalize.return_value = personalized_recommendation

    return DiagnosticService(
        inference_service=inference,
        recommendation_service=recommendation,
        personalization_service=personalization,
        model_version="test-model-v1",
    )


def test_run_diagnostic_without_personalize_leaves_personalized_fields_empty() -> None:
    """personalize=False yields personalized_recommendation=None and used_personalization=False."""
    service = _build_service()

    result = service.run_diagnostic(**CALL_KWARGS, personalize=False)

    assert result.personalized_recommendation is None
    assert result.used_personalization is False


def test_run_diagnostic_with_personalize_success_marks_used_personalization_true() -> None:
    """personalize=True with a succeeding personalization service reports used_personalization=True."""
    service = _build_service(personalized_recommendation="Texto personalizado para el cliente.")

    result = service.run_diagnostic(**CALL_KWARGS, personalize=True)

    assert result.used_personalization is True
    assert result.personalized_recommendation == "Texto personalizado para el cliente."


def test_run_diagnostic_forwards_social_impact_to_personalization_service() -> None:
    """The optional social impact text is forwarded when personalization is requested."""
    service = _build_service(personalized_recommendation="Texto personalizado para el cliente.")

    result = service.run_diagnostic(
        **{
            **CALL_KWARGS,
            "social_impact": "Apoyamos programas de alfabetizacion digital.",
        },
        personalize=True,
    )

    service._personalization_service.personalize.assert_called_once_with(
        sector=CALL_KWARGS["sector"],
        maturity_level="Inicial",
        base_recommendation="Mapear flujos de trabajo.",
        user_response_text=CALL_KWARGS["user_response_text"],
        social_impact="Apoyamos programas de alfabetizacion digital.",
    )
    assert result.used_personalization is True


def test_run_diagnostic_with_personalize_failure_reports_used_personalization_false() -> None:
    """personalize=True but a failing (None-returning) personalization service still reports False.

    This is the single most important test in this file: it verifies the
    distinction between "personalization not requested" and "personalization
    requested but failed", which the orchestrator's contract depends on.
    """
    service = _build_service(personalized_recommendation=None)

    result = service.run_diagnostic(**CALL_KWARGS, personalize=True)

    assert result.used_personalization is False
    assert result.personalized_recommendation is None


def test_diagnostic_id_is_a_valid_uuid_and_differs_across_calls() -> None:
    """diagnostic_id is a valid UUID string, distinct across two separate runs."""
    service = _build_service()

    first = service.run_diagnostic(**CALL_KWARGS, personalize=False)
    second = service.run_diagnostic(**CALL_KWARGS, personalize=False)

    assert uuid.UUID(first.diagnostic_id)
    assert uuid.UUID(second.diagnostic_id)
    assert first.diagnostic_id != second.diagnostic_id


def test_base_recommendation_is_always_populated_regardless_of_personalize_flag() -> None:
    """base_recommendation is present whether or not personalization was requested."""
    service = _build_service(base_recommendation="Estandarizar el registro diario.")

    for personalize in (False, True):
        result = service.run_diagnostic(**CALL_KWARGS, personalize=personalize)
        assert result.base_recommendation == "Estandarizar el registro diario."


def test_recommendation_not_found_error_propagates_from_run_diagnostic() -> None:
    """A RecommendationNotFoundError from the recommendation service is not swallowed.

    The router layer is responsible for translating it into an HTTP
    response; the orchestrator must let it propagate.
    """
    inference = Mock(spec=InferenceService)
    inference.predict.return_value = InferenceResult(
        maturity_level="Inicial",
        class_probabilities={
            "Inicial": 1.0,
            "En Desarrollo": 0.0,
            "Definido": 0.0,
            "Optimizado": 0.0,
        },
    )
    recommendation = Mock(spec=RecommendationService)
    recommendation.get_base_recommendation.side_effect = RecommendationNotFoundError(
        "Agricultura", "Inicial"
    )
    personalization = Mock(spec=PersonalizationService)

    service = DiagnosticService(
        inference_service=inference,
        recommendation_service=recommendation,
        personalization_service=personalization,
        model_version="test-model-v1",
    )

    with pytest.raises(RecommendationNotFoundError):
        service.run_diagnostic(**CALL_KWARGS, personalize=False)
