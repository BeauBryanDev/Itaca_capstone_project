"""Tests for app.services.personalization_service.PersonalizationService.

The real OpenAI client is never constructed with a working call path in
these tests: `_get_client` is monkeypatched wherever a client would be
needed, so no test can reach the network under any circumstance.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.config import Settings
from app.services.personalization_service import PersonalizationService

BASE_CALL_KWARGS = {
    "sector": "Retail",
    "maturity_level": "Inicial",
    "base_recommendation": "Digitalizar el registro de ventas.",
    "user_response_text": "Todo lo llevamos en cuadernos y de memoria.",
    "social_impact": None,
}


def _settings(**overrides) -> Settings:
    defaults = {
        "personalization_enabled": False,
        "openai_api_key": None,
        "openai_model": "gpt-4o",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def test_personalize_returns_none_when_disabled_without_building_client() -> None:
    """When personalization is disabled, personalize() returns None and never builds a client."""
    service = PersonalizationService(_settings(personalization_enabled=False))

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result is None
    assert service._client is None


def test_personalize_returns_none_when_enabled_without_api_key() -> None:
    """Enabled but missing an API key returns None without raising or building a client."""
    service = PersonalizationService(
        _settings(personalization_enabled=True, openai_api_key=None)
    )

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result is None
    assert service._client is None


def test_personalize_returns_none_when_the_openai_call_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure in the (mocked) OpenAI call is caught; personalize() returns None."""
    service = PersonalizationService(
        _settings(personalization_enabled=True, openai_api_key="fake-key")
    )
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = RuntimeError("simulated failure")
    monkeypatch.setattr(service, "_get_client", lambda: mock_client)

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result is None


def test_personalize_returns_generated_text_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A successful (mocked) OpenAI call returns its extracted text content."""
    service = PersonalizationService(
        _settings(personalization_enabled=True, openai_api_key="fake-key")
    )
    mock_message = SimpleNamespace(output_text="Recomendacion personalizada.")
    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_message
    monkeypatch.setattr(service, "_get_client", lambda: mock_client)

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result == "Recomendacion personalizada."


def test_extract_text_returns_output_text_when_available() -> None:
    """_extract_text returns output_text when the SDK exposes it."""
    response = SimpleNamespace(output_text="Primera parte.\nSegunda parte.")

    assert (
        PersonalizationService._extract_text(response)
        == "Primera parte.\nSegunda parte."
    )


def test_extract_text_returns_empty_string_when_no_text_blocks() -> None:
    """_extract_text returns an empty string when no text payload is present."""
    response = SimpleNamespace()

    assert PersonalizationService._extract_text(response) == ""


def test_build_user_prompt_includes_social_impact_when_provided() -> None:
    """The prompt includes the optional social impact context when present."""
    service = PersonalizationService(_settings())

    prompt = service._build_user_prompt(
        sector="Retail",
        maturity_level="Inicial",
        base_recommendation="Digitalizar el registro de ventas.",
        user_response_text="Todo lo llevamos en cuadernos y de memoria.",
        social_impact="Apoyamos programas comunitarios de formación.",
    )

    assert "Labor social / impacto social: Apoyamos programas comunitarios de formación." in prompt
