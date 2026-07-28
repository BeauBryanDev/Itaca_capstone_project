"""Response schema returned by the API after inference and recommendation."""

from datetime import datetime

from pydantic import BaseModel


class DiagnosticoResponse(BaseModel):
    """Result of a diagnostic run: predicted maturity level and recommendation.

    ``class_probabilities`` uses the class names from ``class_map.json``
    (``Inicial``, ``En Desarrollo``, ``Definido``, ``Optimizado``) as keys,
    not the internal integer encoding. Its values are expected to sum to
    approximately 1.0 as a property of the model output; this is not
    enforced by this schema.
    """

    diagnostico_id: str
    maturity_level: str
    class_probabilities: dict[str, float]
    base_recommendation: str
    personalized_recommendation: str | None = None
    used_personalization: bool
    model_version: str
    created_at: datetime
