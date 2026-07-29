
from __future__ import annotations
 
import uuid
from datetime import datetime, timezone
 
from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
 
 
class Base(DeclarativeBase):
    """Shared declarative base for all ORM models in this project."""
 
 
def _generate_uuid() -> str:
    """Generate a new UUID4 string, used as the default primary key value."""
    return str(uuid.uuid4())
 
 
def _utc_now() -> datetime:
    """Return the current UTC timestamp, used as the default created_at value."""
    return datetime.now(timezone.utc)
 
 
class Diagnostic(Base):
    """A single persisted autodiagnostic run.
 
    Stores the client's submitted inputs, the model's prediction,  
    """
 
    __tablename__ = "diagnostics"
 
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_uuid
    )
 
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    company_size: Mapped[str] = mapped_column(String, nullable=False)
    documented_processes_pct: Mapped[float] = mapped_column(Float, nullable=False)
    annual_tech_budget: Mapped[int] = mapped_column(Integer, nullable=False)
    user_response_text: Mapped[str] = mapped_column(Text, nullable=False)
    social_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    predicted_maturity_level: Mapped[str] = mapped_column(String, nullable=False)
    class_probabilities: Mapped[dict] = mapped_column(JSON, nullable=False)
    base_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    personalized_recommendation: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    used_personalization: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    model_version: Mapped[str] = mapped_column(String, nullable=False)
 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
 
    def __repr__(self) -> str:
        
        return (
            f"Diagnostic(id={self.id!r}, sector={self.sector!r}, "
            f"predicted_maturity_level={self.predicted_maturity_level!r})"
        )