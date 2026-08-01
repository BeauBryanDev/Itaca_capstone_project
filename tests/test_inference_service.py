"""Tests for app.services.inference_service.InferenceService."""

from __future__ import annotations

import dataclasses

import pytest

from app.services.inference_service import InferenceResult, InferenceService
from app.utils.artifact_loader import ArtifactRegistry

EXPECTED_CLASSES = {"Inicial", "En Desarrollo", "Definido", "Optimizado"}


def _predict(registry: ArtifactRegistry, **overrides) -> InferenceResult:
    service = InferenceService(registry)
    payload = {
        "sector": "Tecnologia",
        "company_size": "Micro",
        "documented_processes_pct": 0.42,
        "annual_tech_budget": 15_000_000,
        "user_response_text": "Tenemos algunos procesos documentados.",
    }
    payload.update(overrides)
    return service.predict(**payload)


def test_predict_returns_class_probabilities_summing_to_one(registry: ArtifactRegistry) -> None:
    """class_probabilities has exactly the four class names and sums to ~1.0."""
    result = _predict(registry)

    assert set(result.class_probabilities.keys()) == EXPECTED_CLASSES
    assert sum(result.class_probabilities.values()) == pytest.approx(1.0, abs=1e-4)


def test_predicted_level_matches_argmax_of_probabilities(registry: ArtifactRegistry) -> None:
    """maturity_level is the class with the highest reported probability."""
    result = _predict(registry)

    expected = max(result.class_probabilities, key=lambda name: result.class_probabilities[name])
    assert result.maturity_level == expected


def test_predict_succeeds_for_distinct_category_combinations(registry: ArtifactRegistry) -> None:
    """predict() does not raise for at least two distinct (sector, company_size) pairs."""
    first = _predict(registry, sector="Tecnologia", company_size="Micro")
    second = _predict(registry, sector="Retail", company_size="Grande")

    assert first.maturity_level in EXPECTED_CLASSES
    assert second.maturity_level in EXPECTED_CLASSES


def test_predict_does_not_raise_on_out_of_vocabulary_text(registry: ArtifactRegistry) -> None:
    """predict() does not raise when the free text is entirely outside the vocabulary."""
    result = _predict(
        registry,
        user_response_text="Implementamos blockchain y metaverso con criptomonedas cuanticas",
    )

    assert result.maturity_level in EXPECTED_CLASSES


def test_inference_result_is_immutable(registry: ArtifactRegistry) -> None:
    """InferenceResult is a frozen dataclass; reassigning a field raises."""
    result = _predict(registry)

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.maturity_level = "Optimizado"
