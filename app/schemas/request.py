"""Request schema for the diagnostic form submitted by the client."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Sector(str, Enum):
    """Business sector selected by the client in the diagnostic form."""

    TECNOLOGIA = "Tecnologia"
    MANUFACTURA = "Manufactura"
    RETAIL = "Retail"
    SERVICIOS = "Servicios"


class CompanySize(str, Enum):
    """Company size bracket selected by the client in the diagnostic form."""

    MICRO = "Micro"
    PEQUENA = "Pequena"
    MEDIANA = "Mediana"
    GRANDE = "Grande"


class DiagnosticoRequest(BaseModel):
    """Validated payload of a diagnostic form submission."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "Textiles del Norte S.A.S.",
                "sector": "Manufactura",
                "company_size": "Mediana",
                "documented_processes_pct": 0.42,
                "annual_tech_budget": 15000000,
                "user_response_text": (
                    "Tenemos algunos procesos documentados pero la mayoria "
                    "depende de la experiencia del equipo."
                ),
                "personalize": False,
                "social_impact": None,
            }
        }
    )

    company_name: str = Field(..., min_length=1, max_length=200)
    sector: Sector
    company_size: CompanySize
    documented_processes_pct: float = Field(..., ge=0.0, le=1.0)
    annual_tech_budget: int = Field(..., gt=100000)
    user_response_text: str = Field(..., min_length=1)
    personalize: bool = Field(default=False)
    social_impact: str | None = None

    @field_validator("user_response_text")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        """Reject free-text responses that are empty once stripped."""
        if not value.strip():
            raise ValueError("user_response_text must not be empty or whitespace-only")
        return value
