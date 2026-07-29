
from __future__ import annotations
 
from dataclasses import dataclass
 
import numpy as np
import pandas as pd
import tensorflow as tf
 
from app.core.logging import get_logger
from app.utils.artifact_loader import ArtifactRegistry
 
logger = get_logger(__name__)
 
# Column names the one-hot encoder was fitted with. The encoder was fitted
# on a DataFrame with these exact column names, so transform() must receive
# a DataFrame with the same names to guarantee correct column ordering and
# to avoid scikit-learn feature-name warnings.
_CATEGORICAL_COLUMNS = ["sector", "tamano_empresa"]
 
 
@dataclass(frozen=True)
class InferenceResult:
    """Outcome of a single model prediction.
 
    """
 
    maturity_level: str
    class_probabilities: dict[str, float]
 
 
class InferenceService:
    """Runs tabular preprocessing and model inference for a diagnostic.
 
    """
 
    def __init__(self, registry: ArtifactRegistry) -> None:
        self._registry = registry
 
    def _build_tabular_features(
        self,
        sector: str,
        company_size: str,
        documented_processes_pct: float,
        annual_tech_budget: int,
    ) -> np.ndarray:
        """Reproduce the Task A tabular pipeline for a single sample.
 
        The training pipeline produced each tabular row as:
        [2 scaled numeric features] + [8 one-hot categorical features],
        concatenated in that exact order. 
 
        Returns:
            A float32 array of shape (1, 10) ready for the model.
        """
        numeric = np.array(
            [[documented_processes_pct, annual_tech_budget]], dtype="float64"
        )
        scaled_numeric = self._registry.scaler.transform(numeric)
 
        categorical = pd.DataFrame(
            [[sector, company_size]], columns=_CATEGORICAL_COLUMNS
        )
        encoded_categorical = self._registry.onehot_encoder.transform(categorical)
 
        features = np.concatenate([scaled_numeric, encoded_categorical], axis=1)
        
        return features.astype("float32")
 
 
    def predict(
        self,
        sector: str,
        company_size: str,
        documented_processes_pct: float,
        annual_tech_budget: int,
        user_response_text: str,
    ) -> InferenceResult:
        """Predict the maturity level for one client's inputs.
 
        Args:
            sector: Company sector must be a category the encoder knows).
            company_size: Company size (must be a category the encoder kn   ows).
            documented_processes_pct: Fraction of documented processes (0.0-1.0).
            annual_tech_budget: Annual technology budget (positive integer).
            user_response_text: The client's free-text response. Passed to
                the serving model as a raw string; text vectorization is
                embedded in the model graph.
 
        Returns:
            An InferenceResult with the predicted level and the full
            probability distribution.
        """
        tabular_features = self._build_tabular_features(
            sector=sector,
            company_size=company_size,
            documented_processes_pct=documented_processes_pct,
            annual_tech_budget=annual_tech_budget,
        )
 
        # The serving model expects the raw text as a (1, 1) string tensor.
        text_tensor = tf.constant([[user_response_text]], dtype=tf.string)
 
        probabilities = self._registry.serving_model.predict(
            {
                "tabular_input": tf.constant(tabular_features),
                "text_input": text_tensor,
            },
            verbose=0,
        )[0]
 
        predicted_index = int(np.argmax(probabilities))
        maturity_level = self._registry.index_to_class_name(predicted_index)
 
        # Build the probability dictionary keyed by class name, using the
        # class map so the order of keys follows the class indices.
        class_probabilities = {
            self._registry.index_to_class_name(index): float(probabilities[index])
            for index in range(len(probabilities))
        }
 
        logger.info(
            "Inference completed: level=%s confidence=%.4f",
            maturity_level,
            float(np.max(probabilities)),
        )
 
        return InferenceResult(
            maturity_level=maturity_level,
            class_probabilities=class_probabilities,
        )