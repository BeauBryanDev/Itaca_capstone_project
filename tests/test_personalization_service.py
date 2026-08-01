"""Tests for app.services.personalization_service.PersonalizationService.

The real Anthropic client is never constructed with a working call path in
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
}


def _settings(**overrides) -> Settings:
    defaults = {
        "personalization_enabled": False,
        "anthropic_api_key": None,
        "anthropic_model": "claude-haiku-4-5",
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
        _settings(personalization_enabled=True, anthropic_api_key=None)
    )

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result is None
    assert service._client is None


def test_personalize_returns_none_when_the_anthropic_call_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure in the (mocked) Anthropic call is caught; personalize() returns None."""
    service = PersonalizationService(
        _settings(personalization_enabled=True, anthropic_api_key="fake-key")
    )
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = RuntimeError("simulated failure")
    monkeypatch.setattr(service, "_get_client", lambda: mock_client)

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result is None


def test_personalize_returns_generated_text_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A successful (mocked) Anthropic call returns its extracted text content."""
    service = PersonalizationService(
        _settings(personalization_enabled=True, anthropic_api_key="fake-key")
    )
    mock_message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Recomendacion personalizada.")]
    )
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    monkeypatch.setattr(service, "_get_client", lambda: mock_client)

    result = service.personalize(**BASE_CALL_KWARGS)

    assert result == "Recomendacion personalizada."


def test_extract_text_joins_multiple_text_blocks() -> None:
    """_extract_text concatenates every text-type block in the message content."""
    message = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", text="Primera parte."),
            SimpleNamespace(type="text", text="Segunda parte."),
        ]
    )

    assert PersonalizationService._extract_text(message) == "Primera parte.\nSegunda parte."


def test_extract_text_returns_empty_string_when_no_text_blocks() -> None:
    """_extract_text returns an empty string when content has only non-text blocks."""
    message = SimpleNamespace(content=[SimpleNamespace(type="tool_use")])

    assert PersonalizationService._extract_text(message) == ""
