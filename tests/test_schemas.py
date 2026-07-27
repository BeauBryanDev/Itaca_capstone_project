"""Validation tests for the request/response Pydantic schemas."""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import DiagnosticoRequest, DiagnosticoResponse

VALID_REQUEST_PAYLOAD = {
    "company_name": "Textiles del Norte S.A.S.",
    "sector": "Manufactura",
    "company_size": "Mediana",
    "documented_processes_pct": 0.42,
    "annual_tech_budget": 15000000,
    "user_response_text": (
        "Tenemos algunos procesos documentados pero la mayoria depende "
        "de la experiencia del equipo."
    ),
    "personalize": False,
    "social_impact": None,
}


def test_valid_request_passes_validation():
    request = DiagnosticoRequest(**VALID_REQUEST_PAYLOAD)
    assert request.sector == "Manufactura"
    assert request.company_size == "Mediana"


def test_documented_processes_pct_above_one_raises():
    payload = {**VALID_REQUEST_PAYLOAD, "documented_processes_pct": 1.5}
    with pytest.raises(ValidationError):
        DiagnosticoRequest(**payload)


def test_documented_processes_pct_negative_raises():
    payload = {**VALID_REQUEST_PAYLOAD, "documented_processes_pct": -0.1}
    with pytest.raises(ValidationError):
        DiagnosticoRequest(**payload)


def test_annual_tech_budget_below_threshold_raises():
    payload = {**VALID_REQUEST_PAYLOAD, "annual_tech_budget": 50000}
    with pytest.raises(ValidationError):
        DiagnosticoRequest(**payload)


def test_annual_tech_budget_negative_raises():
    payload = {**VALID_REQUEST_PAYLOAD, "annual_tech_budget": -5000000}
    with pytest.raises(ValidationError):
        DiagnosticoRequest(**payload)


def test_invalid_sector_raises():
    payload = {**VALID_REQUEST_PAYLOAD, "sector": "Agricultura"}
    with pytest.raises(ValidationError):
        DiagnosticoRequest(**payload)


def test_valid_response_serializes_to_json():
    response = DiagnosticoResponse(
        diagnostico_id="11111111-1111-1111-1111-111111111111",
        maturity_level="Definido",
        class_probabilities={
            "Inicial": 0.05,
            "En Desarrollo": 0.15,
            "Definido": 0.6,
            "Optimizado": 0.2,
        },
        base_recommendation=(
            "Conectar los datos de produccion en planta con el ERP financiero."
        ),
        personalized_recommendation=None,
        used_personalization=False,
        model_version="1.0.0",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
    )

    payload = json.loads(response.model_dump_json())

    assert payload["maturity_level"] == "Definido"
    assert payload["class_probabilities"]["Optimizado"] == 0.2
    assert payload["used_personalization"] is False
    assert payload["personalized_recommendation"] is None
