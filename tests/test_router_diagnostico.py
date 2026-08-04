"""Tests for the /diagnostico endpoints (app.routers.diagnostico).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

VALID_PAYLOAD = {
    "company_name": "Textiles del Norte S.A.S.",
    "sector": "Manufactura",
    "company_size": "Mediana",
    "documented_processes_pct": 0.42,
    "annual_tech_budget": 15_000_000,
    "user_response_text": (
        "Tenemos algunos procesos documentados pero la mayoria depende de "
        "la experiencia del equipo."
    ),
    "personalize": False,
    "social_impact": None,
}

EXPECTED_RESPONSE_KEYS = {
    "diagnostico_id",
    "maturity_level",
    "class_probabilities",
    "base_recommendation",
    "personalized_recommendation",
    "used_personalization",
    "model_version",
    "created_at",
}
EXPECTED_MATURITY_LEVELS = {"Inicial", "En Desarrollo", "Definido", "Optimizado"}


def test_post_diagnostico_with_valid_payload_returns_201_and_matching_schema(
    client: TestClient,
) -> None:
    """A valid payload returns 201 with every field of DiagnosticoResponse."""
    response = client.post("/diagnostico", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert EXPECTED_RESPONSE_KEYS.issubset(body.keys())
    assert body["maturity_level"] in EXPECTED_MATURITY_LEVELS
    assert body["used_personalization"] is False


def test_created_diagnostic_can_be_retrieved_by_id(client: TestClient) -> None:
    """GET /diagnostico/{id} returns the same maturity_level and class_probabilities as creation."""
    created = client.post("/diagnostico", json=VALID_PAYLOAD).json()

    response = client.get(f"/diagnostico/{created['diagnostico_id']}")

    assert response.status_code == 200
    fetched = response.json()
    assert fetched["maturity_level"] == created["maturity_level"]
    assert fetched["class_probabilities"] == created["class_probabilities"]


def test_get_diagnostico_with_unknown_id_returns_404(client: TestClient) -> None:
    """GET /diagnostico/{id} for a non-existent id returns 404."""
    response = client.get("/diagnostico/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_post_diagnostico_with_pct_above_one_returns_422(client: TestClient) -> None:
    """documented_processes_pct=1.5 fails schema validation before reaching the service."""
    payload = {**VALID_PAYLOAD, "documented_processes_pct": 1.5}

    response = client.post("/diagnostico", json=payload)

    assert response.status_code == 422


def test_post_diagnostico_with_budget_below_threshold_returns_422(client: TestClient) -> None:
    """annual_tech_budget=50000 (below the 100000 threshold) fails schema validation."""
    payload = {**VALID_PAYLOAD, "annual_tech_budget": 50_000}

    response = client.post("/diagnostico", json=payload)

    assert response.status_code == 422


def test_post_diagnostico_with_invalid_sector_returns_422(client: TestClient) -> None:
    """A sector outside the allowed enum fails schema validation."""
    payload = {**VALID_PAYLOAD, "sector": "Agricultura"}

    response = client.post("/diagnostico", json=payload)

    assert response.status_code == 422


def test_successful_post_persists_a_row_in_the_database(
    client: TestClient, db_engine: Engine
) -> None:
    """After a successful POST, the row actually exists in the database.

    Queries the test database directly instead of trusting the HTTP
    response alone, confirming persistence rather than just response
    shaping.
    """
    created = client.post("/diagnostico", json=VALID_PAYLOAD).json()

    with db_engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT sector, predicted_maturity_level FROM diagnostics WHERE id = :id"
            ),
            {"id": created["diagnostico_id"]},
        ).fetchone()

    assert row is not None
    assert row.sector == "Manufactura"
    assert row.predicted_maturity_level == created["maturity_level"]


def test_post_still_returns_result_when_persistence_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed database commit must not discard a valid diagnostic.

    Persistence sits below inference and recommendation in the
    cut-priority order, so a write failure degrades to a non-persisted
    response instead of a 500.
    """

    def failing_commit(self: Session) -> None:
        raise OperationalError("INSERT", {}, Exception("database is locked"))

    monkeypatch.setattr(Session, "commit", failing_commit)

    response = client.post("/diagnostico", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["maturity_level"] in {
        "Inicial",
        "En Desarrollo",
        "Definido",
        "Optimizado",
    }
    assert body["base_recommendation"]
