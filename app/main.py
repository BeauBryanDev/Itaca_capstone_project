
from __future__ import annotations
 
from contextlib import asynccontextmanager
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.models.diagnostic import Base
from app.routers import diagnostico, health, state
from app.services.diagnostico_service import DiagnosticService
from app.services.inference_service import InferenceService
from app.services.personalization_service import PersonalizationService
from app.services.recommendation_service import RecommendationService
from app.utils.artifact_loader import load_all_artifacts
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Assemble every component once, before the app serves any request.

    """
    settings = get_settings()
 
    setup_logging(debug=settings.debug)
    logger = get_logger(__name__)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
 
    # Fail fast if personalization is enabled without an API key.
    settings.validate_personalization_config()
 
    # load runtime artifacts.
    logger.info("Loading artifacts from %s", settings.artifacts_dir)
    registry = load_all_artifacts(settings.artifacts_dir)
    logger.info("Artifacts loaded. Model version: %s", registry.model_version)
 
    #  build domain services in dependency order.
    inference = InferenceService(registry)
    recommendation = RecommendationService(registry)
    personalization = PersonalizationService(settings)
 
    # build the orchestrator.
    diagnostic_service = DiagnosticService(
        inference_service=inference,
        recommendation_service=recommendation,
        personalization_service=personalization,
        model_version=registry.model_version,
    )
 
    #  database engine and schema.
    connect_args = (
        {"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {}
    )
    engine = create_engine(settings.database_url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    logger.info("Database ready at %s", settings.database_url)
 
    # S register singletons into shared state for the routers.
    state.set_diagnostic_service(diagnostic_service)
    state.set_session_factory(session_factory)
 
    logger.info("Startup complete. Application is ready to serve requests.")
 
    yield
 
    # Shutdown: dispose of the database engine cleanly.
    engine.dispose()
    
    logger.info("Shutdown complete.")
    


 
def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
 
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
 
    app.include_router(health.router)
    app.include_router(diagnostico.router)
 
    return app
 
 
app = create_app()
 
 
 