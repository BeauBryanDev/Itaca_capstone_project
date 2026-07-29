
from __future__ import annotations
 
from datetime import datetime
 
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
 
from diagnostic_model import Base, Diagnostic
 
 
@pytest.fixture
def engine() -> Engine:
    """Create a fresh in-memory SQLite engine with the schema applied."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)
    return test_engine
 
 
@pytest.fixture
def sample_diagnostic() -> Diagnostic:
    """Build a Diagnostic instance with representative values, not yet persisted."""
    return Diagnostic(
        company_name="Panaderia El Trigal",
        sector="Retail",
        company_size="Micro",
        documented_processes_pct=0.15,
        annual_tech_budget=4_000_000,
        user_response_text="Todo lo llevamos en cuadernos y de memoria.",
        social_impact=None,
        predicted_maturity_level="Inicial",
        class_probabilities={
            "Inicial": 0.91,
            "En Desarrollo": 0.06,
            "Definido": 0.02,
            "Optimizado": 0.01,
        },
        base_recommendation="Digitalizar el registro de ventas.",
        personalized_recommendation=None,
        model_version="v1.0.0",
    )
 
 
def test_insert_and_read_back(engine: Engine, sample_diagnostic: Diagnostic) -> None:
    """A Diagnostic row is persisted and read back with identical values."""
    with Session(engine) as session:
        session.add(sample_diagnostic)
        session.commit()
 
    with Session(engine) as session:
        stored = session.query(Diagnostic).one()
 
        assert stored.id is not None
        assert stored.company_name == "Panaderia El Trigal"
        assert stored.sector == "Retail"
        assert stored.company_size == "Micro"
        assert stored.documented_processes_pct == 0.15
        assert stored.annual_tech_budget == 4_000_000
        assert stored.predicted_maturity_level == "Inicial"
        assert stored.class_probabilities["Inicial"] == 0.91
        assert stored.base_recommendation == "Digitalizar el registro de ventas."
        assert stored.social_impact is None
        assert stored.personalized_recommendation is None
 
 
def test_defaults_are_applied(engine: Engine, sample_diagnostic: Diagnostic) -> None:
    """Columns with a default (used_personalization, created_at) are populated."""
    with Session(engine) as session:
        session.add(sample_diagnostic)
        session.commit()
 
    with Session(engine) as session:
        stored = session.query(Diagnostic).one()
 
        assert stored.used_personalization is False
        assert isinstance(stored.created_at, datetime)
 
 
def test_repr_is_readable(sample_diagnostic: Diagnostic) -> None:
    """The repr includes enough context to identify the row during debugging."""
    text = repr(sample_diagnostic)
 
    assert "Diagnostic" in text
    assert "Retail" in text
    assert "Inicial" in text
 