from __future__ import annotations
 
from fastapi import APIRouter
 
from app.core.config import get_settings
from app.routers import state
 
router = APIRouter(tags=["health"])
 
 
@router.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the application is up and its dependencies are ready.
    """
    settings = get_settings()
 
    # Touch the diagnostic service dependency to confirm it is initialized.
    # If startup failed to build it, this raises and the endpoint reports
    # unhealthy rather than falsely claiming readiness.
    service_ready = state._diagnostic_service is not None
 
    return {
        "status": "ok" if service_ready else "initializing",
        "app": settings.app_name,
        "version": settings.app_version,
        
        "model_version": (
            
            state._diagnostic_service._model_version
            if service_ready
            else "unknown"
        ),
    }