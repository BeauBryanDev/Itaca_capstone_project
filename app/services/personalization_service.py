from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# System prompt that frames the model's task. Kept module-level so it is
# defined once and is easy to review and adjust.
_SYSTEM_PROMPT = (
    "Eres un consultor de transformacion organizacional. Tu tarea es "
    "reescribir una recomendacion base para que sea especifica y accionable "
    "para un cliente concreto, considerando su sector y la descripcion que "
    "el cliente hizo de su situacion. Manten la recomendacion breve (dos a "
    "cuatro frases), en espanol, en un tono profesional y directo. No "
    "inventes datos que el cliente no haya mencionado y no cambies el "
    "sentido de la recomendacion base."
)


class PersonalizationService:
    """Generates a personalized recommendation using an OpenAI model."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None  # created lazily in _get_client

    def _get_client(self):
        """Return a cached OpenAI client, creating it on first use."""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self._settings.openai_api_key)
        return self._client

    def _build_user_prompt(
        self,
        sector: str,
        maturity_level: str,
        base_recommendation: str,
        user_response_text: str,
        social_impact: str | None = None,
    ) -> str:
        """Assemble the user-facing prompt with the diagnostic context."""
        social_impact_section = (
            f"Labor social / impacto social: {social_impact}\n"
            if social_impact and social_impact.strip()
            else ""
        )

        return (
            f"Sector del cliente: {sector}\n"
            f"Nivel de madurez diagnosticado: {maturity_level}\n"
            f"Descripcion del cliente: {user_response_text}\n"
            f"{social_impact_section}"
            f"Recomendacion base a personalizar: {base_recommendation}\n\n"
            "Reescribe la recomendacion base personalizada para este cliente, "
            "teniendo en cuenta cualquier labor social o impacto social "
            "relevante cuando exista."
        )

    def personalize(
        self,
        sector: str,
        maturity_level: str,
        base_recommendation: str,
        user_response_text: str,
        social_impact: str | None = None,
    ) -> str | None:
        """Return a personalized recommendation, or None on any failure.

        The service never raises. It returns None when personalization is
        disabled, when the API key is missing, or when the OpenAI call fails.
        """
        if not self._settings.personalization_enabled:
            logger.debug("Personalization disabled by configuration; skipping.")
            return None

        if not self._settings.openai_api_key:
            logger.warning(
                "Personalization enabled but no API key is set; falling back "
                "to base recommendation."
            )
            return None

        user_prompt = self._build_user_prompt(
            sector=sector,
            maturity_level=maturity_level,
            base_recommendation=base_recommendation,
            user_response_text=user_response_text,
            social_impact=social_impact,
        )

        try:
            client = self._get_client()
            response = client.responses.create(
                model=self._settings.openai_model,
                instructions=_SYSTEM_PROMPT,
                input=user_prompt,
                max_output_tokens=400,
            )
            personalized = self._extract_text(response)

            if not personalized:
                logger.warning(
                    "OpenAI response contained no text; falling back to base "
                    "recommendation."
                )
                return None

            logger.info("Personalized recommendation generated successfully.")
            return personalized
        except Exception as exc:
            # Any failure (network, auth, rate limit, malformed response) is
            # caught here so the orchestrator can fall back cleanly. The
            # error is logged but never propagated to the request handler.
            logger.warning(
                "Personalization failed (%s); falling back to base "
                "recommendation.",
                type(exc).__name__,
            )
            return None

    @staticmethod
    def _extract_text(response) -> str:
        """Extract the final text payload from an OpenAI response."""
        output_text = getattr(response, "output_text", "")
        
        if isinstance(output_text, str):
            
            return output_text.strip()
        
        return ""
