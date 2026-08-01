from __future__ import annotations
 
from app.core.logging import get_logger
from app.utils.artifact_loader import ArtifactRegistry
 
logger = get_logger(__name__)
 


class RecommendationNotFoundError(RuntimeError):
    """Raised when no catalog entry exists for a (sector, level) pair."""
    
    def __init__(self, sector: str, level: str) -> None:
        super().__init__(f"No recommendation found for {sector} {level}")
        self.sector = sector
        self.level = level
        
        

class RecommendationService:
    """Looks up the deterministic base recommendation for a diagnostic."""
 
    def __init__(self, registry: ArtifactRegistry) -> None:
        self._registry = registry
        # Build an in-memory index once, so each lookup is a dictionary
        # access instead of a DataFrame filter. The key is the
        # (sector, maturity_level) pair; the value is the recommendation text.
        self._index = self._build_index()
 
    def _build_index(self) -> dict[tuple[str, str], str]:
        """Index the catalog by (sector, maturity_level) for O(1) lookups."""
        catalog = self._registry.recommendation_catalog
        
        index: dict[tuple[str, str], str] = {}
        
        for row in catalog.itertuples(index=False):
            
            key = (row.sector, row.nivel_madurez)
            
            index[key] = row.recomendacion
            
        logger.info("Recommendation catalog indexed: %d entries", len(index))
        
        return index
 
 
    def get_base_recommendation(self, sector: str, maturity_level: str) -> str:
        """Return the base recommendation for a (sector, maturity_level) pair.
 
        """ 
        
        key = (sector, maturity_level)
        
        recommendation = self._index.get(key)
        
        if recommendation is None:

            raise RecommendationNotFoundError(sector, maturity_level)

        return recommendation
 
 
 