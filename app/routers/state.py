
from __future__ import annotations
 
from typing import Callable
 
from fastapi import Depends
from sqlalchemy.orm import Session
 
from app.services.diagnostico_service import DiagnosticService
 
_diagnostic_service: DiagnosticService | None = None
_session_factory: Callable[[], Session] | None = None
 
 
def set_diagnostic_service(service: DiagnosticService) -> None:
    """Register the diagnostic orchestrator built at startup."""
    global _diagnostic_service
    _diagnostic_service = service
 
 
def set_session_factory(factory: Callable[[], Session]) -> None:
    """Register the database session factory built at startup."""
    global _session_factory
    _session_factory = factory
 
 
def get_diagnostic_service() -> DiagnosticService:
    """FastAPI dependency that returns the diagnostic orchestrator.
 
    Raises:
        RuntimeError: If called before the startup event registered the
            service.
    """
    if _diagnostic_service is None:
        raise RuntimeError(
            "DiagnosticService is not initialized. The application startup "
            "event must run before handling requests."
        )
    return _diagnostic_service
 
 
def get_db_session():
    """FastAPI dependency that yields a database session and closes it.
 
    Yields:
        An open SQLAlchemy Session that is committed by the caller and
        always closed when the request finishes.
 
    Raises:
        RuntimeError: If called before the startup event registered the
            session factory.
    """
    if _session_factory is None:
        raise RuntimeError(
            "Session factory is not initialized. The application startup "
            "event must run before handling requests."
        )
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
 