"""Tests for app.services.recommendation_service.RecommendationService."""

from __future__ import annotations

import pytest

from app.services.recommendation_service import (
    RecommendationNotFoundError,
    RecommendationService,
)
from app.utils.artifact_loader import ArtifactRegistry


def test_get_base_recommendation_returns_expected_text_for_known_pair(
    registry: ArtifactRegistry,
) -> None:
    """A known (sector, maturity_level) pair returns the catalog's exact text."""
    service = RecommendationService(registry)

    recommendation = service.get_base_recommendation(
        sector="Tecnologia", maturity_level="Inicial"
    )

    assert recommendation == "Recomendacion de prueba para Tecnologia / Inicial."


def test_unknown_sector_raises_recommendation_not_found_error(
    registry: ArtifactRegistry,
) -> None:
    """A sector absent from the catalog raises RecommendationNotFoundError."""
    service = RecommendationService(registry)

    with pytest.raises(RecommendationNotFoundError):
        service.get_base_recommendation(sector="Agricultura", maturity_level="Inicial")


def test_unknown_maturity_level_raises_recommendation_not_found_error(
    registry: ArtifactRegistry,
) -> None:
    """A maturity level absent from the catalog raises RecommendationNotFoundError, even for a known sector."""
    service = RecommendationService(registry)

    with pytest.raises(RecommendationNotFoundError):
        service.get_base_recommendation(sector="Tecnologia", maturity_level="Nivel Inexistente")


def test_catalog_is_indexed_once_and_does_not_track_a_live_dataframe(
    registry: ArtifactRegistry,
) -> None:
    """Lookups keep working after the registry's DataFrame is emptied.

    The service builds its own index at construction time; it must not
    hold a live reference to the registry's DataFrame that would make
    lookups fail if that DataFrame were later mutated or cleared.
    """
    service = RecommendationService(registry)

    registry.recommendation_catalog.drop(registry.recommendation_catalog.index, inplace=True)
    assert len(registry.recommendation_catalog) == 0

    recommendation = service.get_base_recommendation(
        sector="Retail", maturity_level="Optimizado"
    )

    assert recommendation == "Recomendacion de prueba para Retail / Optimizado."
