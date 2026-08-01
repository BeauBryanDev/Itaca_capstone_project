"""Tests for the GET /health endpoint (app.routers.health)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FIXTURE_MODEL_VERSION


def test_health_returns_ok_when_the_app_started_successfully(client: TestClient) -> None:
    """GET /health returns 200 and status "ok" once the real lifespan has run."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_reports_the_model_version_from_metadata(client: TestClient) -> None:
    """The response's model_version matches the fixture model_metadata.json."""
    response = client.get("/health")

    assert response.json()["model_version"] == FIXTURE_MODEL_VERSION
