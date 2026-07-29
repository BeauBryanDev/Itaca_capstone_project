
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
    """Generates a personalized recommendation using an Anthropic model.
    """
 
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None  # created lazily in _get_client
 
    def _get_client(self):
        """Return a cached Anthropic client, creating it on first use.
 
        Imports the anthropic SDK inside the method so the dependency is
        only required when personalization is actually used.
        """
        if self._client is None:
            from anthropic import Anthropic
 
            self._client = Anthropic(api_key=self._settings.anthropic_api_key)
        return self._client
 
    def _build_user_prompt(
        self,
        sector: str,
        maturity_level: str,
        base_recommendation: str,
        user_response_text: str,
    ) -> str:
        """Assemble the user-facing prompt with the diagnostic context."""
        return (
            f"Sector del cliente: {sector}\n"
            f"Nivel de madurez diagnosticado: {maturity_level}\n"
            f"Descripcion del cliente: {user_response_text}\n"
            f"Recomendacion base a personalizar: {base_recommendation}\n\n"
            "Reescribe la recomendacion base personalizada para este cliente."
        )
 
    def personalize(
        self,
        sector: str,
        maturity_level: str,
        base_recommendation: str,
        user_response_text: str,
    ) -> str | None:
        """Return a personalized recommendation, or None on any failure.
 
        Args:
            sector: The company sector.
            maturity_level: The predicted maturity level.
            base_recommendation: The deterministic recommendation to rewrite.
            user_response_text: The client's free-text description.
 
        Returns:
            The personalized recommendation text, or None if personalization
            is disabled or the API call failed. Never raises.
        """
        if not self._settings.personalization_enabled:
            logger.debug("Personalization disabled by configuration; skipping.")
            return None
 
        if not self._settings.anthropic_api_key:
            logger.warning(
                "Personalization enabled but no API key is set; "
                "falling back to base recommendation."
            )
            
            return None
 
        user_prompt = self._build_user_prompt(
            sector=sector,
            maturity_level=maturity_level,
            base_recommendation=base_recommendation,
            user_response_text=user_response_text,
        )
 
        try:
            
            client = self._get_client()
            
            message = client.messages.create(
                
                model=self._settings.anthropic_model,
                max_tokens=400,
                
                system=_SYSTEM_PROMPT,
                
                messages=[{"role": "user", "content": user_prompt}],
            )
            personalized = self._extract_text(message)
            
            if not personalized:
                
                logger.warning(
                    
                    "Anthropic response contained no text; "
                    "falling back to base recommendation."
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
    def _extract_text(message) -> str:
        
        """Extract and join text blocks from an Anthropic message response."""
        parts = [
            
            block.text
            
            for block in message.content
            
            if getattr(block, "type", None) == "text"
        ]
        
        return "\n".join(parts).strip()
 