"""Shared pytest fixtures for the Itaca SmartDiag backend test suite.

Builds a minimal but structurally valid set of runtime artifacts (a tiny
Keras serving model, a fitted scaler/encoder, a class map, a recommendation
catalog, and metadata) so the suite never depends on the real multi-hundred
KB trained model, on Google Drive, or on any network access.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Callable, Iterator

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import Engine, create_engine

from app.core.config import get_settings
from app.main import create_app
from app.utils.artifact_loader import ArtifactRegistry, load_all_artifacts

# The exact class map every layer of the system (schemas, model, catalog)
# is built around. Kept in one place so fixtures cannot drift from it.
CLASS_MAP = {"Inicial": 0, "En Desarrollo": 1, "Definido": 2, "Optimizado": 3}
SECTORS = ["Tecnologia", "Manufactura", "Retail", "Servicios"]
COMPANY_SIZES = ["Micro", "Pequena", "Mediana", "Grande"]

# model_metadata.json's model_name in the fixture artifacts, asserted
# against by router tests that check the /health response.
FIXTURE_MODEL_VERSION = "itaca-fixture-model"


def _build_tiny_serving_model():
    """Build a structurally valid but untrained multimodal Keras model.

    Mirrors the real serving model's I/O contract exactly: a
    ``tabular_input`` of shape (10,) float32, a ``text_input`` of shape (1,)
    string, and a 4-class softmax output. Random weights are fine here —
    these fixtures test the plumbing (shapes, dtypes, service wiring), not
    predictive accuracy, which is validated separately in the training
    notebook and metrics report.
    """
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    vectorizer = layers.TextVectorization(
        max_tokens=20,
        output_mode="int",
        output_sequence_length=8,
        standardize="lower_and_strip_punctuation",
    )
    # set_vocabulary() auto-prepends the padding/OOV reserved tokens, so
    # only real words are passed here (mirrors the training notebook).
    vectorizer.set_vocabulary(["proceso", "empresa", "documentado", "manual"])

    tabular_input = keras.Input(shape=(10,), dtype="float32", name="tabular_input")
    text_input = keras.Input(shape=(1,), dtype=tf.string, name="text_input")

    tab_branch = layers.Dense(4, activation="relu")(tabular_input)

    text_ids = vectorizer(text_input)
    text_branch = layers.Embedding(input_dim=20, output_dim=4, mask_zero=True)(text_ids)
    text_branch = layers.GlobalAveragePooling1D()(text_branch)

    fused = layers.Concatenate()([tab_branch, text_branch])
    output = layers.Dense(4, activation="softmax", name="output")(fused)

    return keras.Model(inputs=[tabular_input, text_input], outputs=output)


def _build_fitted_scaler() -> StandardScaler:
    """Fit a StandardScaler on the same two numeric columns as production."""
    scaler = StandardScaler()
    dummy = pd.DataFrame(
        {
            "porcentaje_procesos_documentados": [0.1, 0.4, 0.6, 0.9],
            "presupuesto_anual_tecnologia": [1_000_000, 5_000_000, 20_000_000, 90_000_000],
        }
    )
    scaler.fit(dummy)
    return scaler


def _build_fitted_encoder() -> OneHotEncoder:
    """Fit a OneHotEncoder covering every real sector and company size."""
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    dummy = pd.DataFrame({"sector": SECTORS, "tamano_empresa": COMPANY_SIZES})
    encoder.fit(dummy)
    return encoder


def build_recommendation_catalog() -> pd.DataFrame:
    """Build the full 16-row (sector, maturity_level) recommendation catalog."""
    rows = [
        {
            "sector": sector,
            "nivel_madurez": level,
            "recomendacion": f"Recomendacion de prueba para {sector} / {level}.",
        }
        for sector in SECTORS
        for level in CLASS_MAP
    ]
    return pd.DataFrame(rows)


def _write_artifacts(
    directory: Path,
    shared_model_path: Path,
    exclude: frozenset[str],
) -> Path:
    """Write a complete set of runtime artifacts into ``directory``.

    Any file name present in ``exclude`` (matching the on-disk names used
    by ``app.utils.artifact_loader``) is skipped, so tests can build
    directories that are missing a specific artifact.
    """
    directory.mkdir(parents=True, exist_ok=True)

    if "itaca_serving.keras" not in exclude:
        shutil.copy2(shared_model_path, directory / "itaca_serving.keras")

    if "scaler.joblib" not in exclude:
        joblib.dump(_build_fitted_scaler(), directory / "scaler.joblib")

    if "onehot_encoder.joblib" not in exclude:
        joblib.dump(_build_fitted_encoder(), directory / "onehot_encoder.joblib")

    if "class_map.json" not in exclude:
        (directory / "class_map.json").write_text(
            json.dumps(CLASS_MAP, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if "catalogo_recomendaciones.csv" not in exclude:
        build_recommendation_catalog().to_csv(
            directory / "catalogo_recomendaciones.csv", index=False, encoding="utf-8"
        )

    if "model_metadata.json" not in exclude:
        metadata = {"model_name": FIXTURE_MODEL_VERSION}
        (directory / "model_metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return directory


@pytest.fixture(scope="session")
def shared_serving_model_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the tiny Keras serving model once per test session.

    Building and saving a Keras model has real overhead (TF graph
    construction). Every test that needs the artifact copies this single
    saved file instead of rebuilding the model from scratch.
    """
    directory = tmp_path_factory.mktemp("shared_model")
    model = _build_tiny_serving_model()
    path = directory / "itaca_serving.keras"
    model.save(path)
    return path


@pytest.fixture
def build_artifacts_dir(
    tmp_path: Path, shared_serving_model_path: Path
) -> Callable[..., Path]:
    """Return a factory that (re)builds a fixture artifacts directory.

    Usage: ``build_artifacts_dir()`` for a complete valid directory, or
    ``build_artifacts_dir(exclude={"scaler.joblib"})`` to omit one file,
    for tests that exercise the artifact loader's failure paths.
    """

    def _build(exclude: frozenset[str] = frozenset(), name: str = "artifacts") -> Path:
        return _write_artifacts(tmp_path / name, shared_serving_model_path, exclude)

    return _build


@pytest.fixture
def test_artifacts_dir(build_artifacts_dir: Callable[..., Path]) -> Path:
    """A complete, valid runtime artifacts directory, fresh for each test."""
    return build_artifacts_dir()


@pytest.fixture
def registry(test_artifacts_dir: Path) -> ArtifactRegistry:
    """An ArtifactRegistry loaded from the fixture artifacts directory."""
    return load_all_artifacts(test_artifacts_dir)


@pytest.fixture
def app_env(
    tmp_path: Path, test_artifacts_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Path]:
    """Point the application's settings at fixture artifacts and an isolated DB.

    Yields the SQLite file path so tests can open a second, independent
    connection to verify persistence directly against the database,
    instead of trusting the HTTP response alone.
    """
    db_path = tmp_path / "test_app.db"
    monkeypatch.setenv("ARTIFACTS_DIR", str(test_artifacts_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("PERSONALIZATION_ENABLED", "false")
    get_settings.cache_clear()
    yield db_path
    get_settings.cache_clear()


@pytest.fixture
def client(app_env: Path) -> Iterator[TestClient]:
    """A TestClient built from the real app, with the real lifespan applied.

    Router tests exercise the actual startup wiring (artifact loading,
    service assembly, DB schema creation) instead of a hand-assembled
    shortcut.
    """
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def db_engine(app_env: Path) -> Iterator[Engine]:
    """A second SQLAlchemy engine over the same on-disk test database.

    Lets tests query rows the API created directly, independent of the
    app's own session factory, to verify actual persistence rather than
    just response shaping.
    """
    engine = create_engine(f"sqlite:///{app_env}")
    yield engine
    engine.dispose()
