
from __future__ import annotations
 
from functools import lru_cache
from pathlib import Path
 
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
 

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
 
 
class Settings(BaseSettings):
    """Runtime configuration for the Itaca SmartDiag backend.
 
    """
 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
 
    #  Application metadata 
    app_name: str = "Itaca SmartDiag API"
    app_version: str = "0.1.0"
    debug: bool = False
 
    #  Artifact paths 
    # Directory containing the runtime artifacts 
    artifacts_dir: Path = _PROJECT_ROOT / "artifacts"
 
    #  Database 
    # Full SQLAlchemy connection string. Defaults to a local SQLite file
    database_url: str = f"sqlite:///{_PROJECT_ROOT / 'itaca_smartdiag.db'}"
 
    #  LLM personalization layer
    personalization_enabled: bool = False
    openai_api_key: str | None = Field(default=None, repr=False)
    openai_model: str = "gpt-4o"
 
    #  CORS  
    # Origins allowed to call this API from a browser.  
    cors_allowed_origins: list[str] = ["http://localhost:5173"]
 
    def validate_personalization_config(self) -> None:
        """Raise a clear error if personalization is enabled without an API key..
 
        Raises:
            ValueError: If personalization_enabled is True but no API key
                was provided.
        """
        if self.personalization_enabled and not self.openai_api_key:
            raise ValueError(
                "personalization_enabled is True but openai_api_key is "
                "not set. Provide OPENAI_API_KEY as an environment "
                "variable, or set PERSONALIZATION_ENABLED=false."
            )
 
 
@lru_cache
def get_settings() -> Settings:
    """Return the application settings, loaded once and cached.
 
    """
    return Settings()
