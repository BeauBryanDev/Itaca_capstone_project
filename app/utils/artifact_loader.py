from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
 
import joblib
import pandas as pd
from tensorflow import keras


class ArtifactLoadError(RuntimeError):
    """Raised when a required artifact is missing or fails to load.
    """
 
@dataclass(frozen=True)
class ArtifactRegistry:
    """Holds every artifact required to run inference and recommendations."""

    serving_model: keras.Model
    scaler: Any
    onehot_encoder: Any
    class_map: dict[str, int]
    recommendation_catalog: pd.DataFrame
    model_version: str
    index_to_class: dict[int, str] = field(init=False)

    def __post_init__(self) -> None:
 
        inverted = {index: name for name, index in self.class_map.items()}
        
        object.__setattr__(self, "index_to_class", inverted)
        

    def index_to_class_name(self, index: int) -> str:
        
        """Return the class name associated with a predicted class index."""
        try:
            
            return self.index_to_class[index]
        
        except KeyError as exc:
            
            raise KeyError(f"No class name found for index {index} in class_map") from exc
 

 
def _require_file(path: Path) -> Path:
    """Return path if it exists as a file, otherwise raise ArtifactLoadError."""
    if not path.is_file():
        
        raise ArtifactLoadError(
            f"Required artifact not found: {path}. "
            "Check that the artifacts directory was populated correctly "
            "before starting the application."
        )
    return path



def load_serving_model(artifacts_dir: Path) -> keras.Model:
    """Load the Keras serving model.
 
    The serving model is expected to accept raw tabular features and raw
    text strings directly (text vectorization is embedded in the model
    graph), so no separate vocabulary file needs to be loaded here.
    """
    model_path = _require_file(artifacts_dir / "itaca_serving.keras")
    
    try:
        
        return keras.models.load_model(model_path)
    
    except Exception as exc:
        
        raise ArtifactLoadError(
            
            f"Failed to load serving model from {model_path}: {exc}"
        ) from exc
 
 
def load_scaler(artifacts_dir: Path) -> Any:
    """Load the fitted StandardScaler used for numeric tabular features."""
    scaler_path = _require_file(artifacts_dir / "scaler.joblib")
    
    try:
        
        return joblib.load(scaler_path)
    
    except Exception as exc:
        
        raise ArtifactLoadError(
            
            f"Failed to load scaler from {scaler_path}: {exc}"
        ) from exc
 
 
def load_onehot_encoder(artifacts_dir: Path) -> Any:
    """Load the fitted OneHotEncoder used for categorical tabular features."""
    encoder_path = _require_file(artifacts_dir / "onehot_encoder.joblib")
    
    try:
        
        return joblib.load(encoder_path)
    
    except Exception as exc:
        
        raise ArtifactLoadError(
            
            f"Failed to load one-hot encoder from {encoder_path}: {exc}"
        ) from exc
 
 

def load_class_map(artifacts_dir: Path) -> dict[str, int]:
    """Load the class name to class index mapping.
 
    Raises:
        ArtifactLoadError: If the file is missing, malformed, or does not
            contain exactly the four expected maturity level classes.
    """
    class_map_path = _require_file(artifacts_dir / "class_map.json")
    
    try:
        
        with class_map_path.open(encoding="utf-8") as file:
            class_map = json.load(file)
            
    except (OSError, json.JSONDecodeError) as exc:
        
        raise ArtifactLoadError(
            
            f"Failed to parse class map from {class_map_path}: {exc}"
        ) from exc
 
    expected_classes = {"Inicial", "En Desarrollo", "Definido", "Optimizado"}
    
    if set(class_map.keys()) != expected_classes:
        
        raise ArtifactLoadError(
            
            f"class_map.json does not contain the expected classes. "
            f"Expected {expected_classes}, found {set(class_map.keys())}."
        )
        
    return class_map
 
 
def load_recommendation_catalog(artifacts_dir: Path) -> pd.DataFrame:
    """Load the deterministic (sector, maturity_level) -> recommendation catalog."""
    catalog_path = _require_file(artifacts_dir / "catalogo_recomendaciones.csv")
    
    try:
        
        catalog = pd.read_csv(catalog_path, encoding="utf-8")
        
    except Exception as exc:
        
        raise ArtifactLoadError(
            
            f"Failed to read recommendation catalog from {catalog_path}: {exc}"
        ) from exc
 
    required_columns = {"sector", "nivel_madurez", "recomendacion"}
    
    if not required_columns.issubset(catalog.columns):
        
        raise ArtifactLoadError(
            
            f"Recommendation catalog is missing required columns. "
            f"Expected at least {required_columns}, found {set(catalog.columns)}."
        )
        
    return catalog



def load_model_version(artifacts_dir: Path) -> str:
    """Read the model version identifier from the model metadata file.
 
    Falls back to "unknown" instead of raising, since the model version is
    used only for traceability in API responses and its absence should not
    prevent the application from starting.
    """
    metadata_path = artifacts_dir / "model_metadata.json"
    
    if not metadata_path.is_file():
        
        return "unknown"
 
    try:
        
        with metadata_path.open(encoding="utf-8") as file:
            
            metadata = json.load(file)
            
        return str(metadata.get("model_name", "unknown"))
    
    except (OSError, json.JSONDecodeError):
        
        return "unknown"
 
 

def load_all_artifacts(artifacts_dir: Path) -> ArtifactRegistry:
    """Load every runtime artifact and return them as a single registry.
 
    Args:
        artifacts_dir: Directory containing all artifact files.
 
    Returns:
        A fully populated ArtifactRegistry.
 
    Raises:
        ArtifactLoadError: If any required artifact cannot be loaded.
    """
    if not artifacts_dir.is_dir():
        
        raise ArtifactLoadError(
            
            f"Artifacts directory does not exist: {artifacts_dir}"
        )
 
    return ArtifactRegistry(
        
        serving_model=load_serving_model(artifacts_dir),
        
        scaler=load_scaler(artifacts_dir),
        
        onehot_encoder=load_onehot_encoder(artifacts_dir),
        
        class_map=load_class_map(artifacts_dir),
        
        recommendation_catalog=load_recommendation_catalog(artifacts_dir),
        
        model_version=load_model_version(artifacts_dir),
        
    )
 