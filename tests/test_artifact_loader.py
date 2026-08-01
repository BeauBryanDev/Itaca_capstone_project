"""Tests for app.utils.artifact_loader: loading and validating runtime artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from app.utils.artifact_loader import ArtifactLoadError, load_all_artifacts


def test_load_all_artifacts_succeeds_with_complete_directory(test_artifacts_dir: Path) -> None:
    """A complete, valid artifacts directory produces a fully populated registry."""
    registry = load_all_artifacts(test_artifacts_dir)

    assert registry.serving_model is not None
    assert registry.scaler is not None
    assert registry.onehot_encoder is not None
    assert registry.class_map == {
        "Inicial": 0,
        "En Desarrollo": 1,
        "Definido": 2,
        "Optimizado": 3,
    }
    assert len(registry.recommendation_catalog) == 16
    assert registry.model_version == "itaca-fixture-model"


def test_missing_scaler_raises_artifact_load_error(
    build_artifacts_dir: Callable[..., Path],
) -> None:
    """A missing scaler.joblib raises ArtifactLoadError naming that file."""
    directory = build_artifacts_dir(exclude=frozenset({"scaler.joblib"}))

    with pytest.raises(ArtifactLoadError, match="scaler.joblib"):
        load_all_artifacts(directory)


def test_missing_onehot_encoder_raises_artifact_load_error(
    build_artifacts_dir: Callable[..., Path],
) -> None:
    """A missing onehot_encoder.joblib raises ArtifactLoadError naming that file."""
    directory = build_artifacts_dir(exclude=frozenset({"onehot_encoder.joblib"}))

    with pytest.raises(ArtifactLoadError, match="onehot_encoder.joblib"):
        load_all_artifacts(directory)


def test_missing_serving_model_raises_artifact_load_error(
    build_artifacts_dir: Callable[..., Path],
) -> None:
    """A missing itaca_serving.keras raises ArtifactLoadError naming that file."""
    directory = build_artifacts_dir(exclude=frozenset({"itaca_serving.keras"}))

    with pytest.raises(ArtifactLoadError, match="itaca_serving.keras"):
        load_all_artifacts(directory)


def test_class_map_with_wrong_classes_raises_artifact_load_error(
    build_artifacts_dir: Callable[..., Path],
) -> None:
    """A class_map.json with an incorrect set of classes raises ArtifactLoadError."""
    directory = build_artifacts_dir(exclude=frozenset({"class_map.json"}))
    bad_map = '{"Iniciial": 0, "En Desarrollo": 1, "Definido": 2, "Optimizado": 3}'
    (directory / "class_map.json").write_text(bad_map, encoding="utf-8")

    with pytest.raises(ArtifactLoadError, match="expected classes"):
        load_all_artifacts(directory)


def test_nonexistent_artifacts_directory_raises_before_reading_files(tmp_path: Path) -> None:
    """A non-existent artifacts directory raises before any file is read."""
    missing_dir = tmp_path / "does_not_exist"

    with pytest.raises(ArtifactLoadError, match="does not exist"):
        load_all_artifacts(missing_dir)


def test_index_to_class_name_resolves_all_four_indices(test_artifacts_dir: Path) -> None:
    """index_to_class_name returns the correct class name for indices 0-3."""
    registry = load_all_artifacts(test_artifacts_dir)

    assert registry.index_to_class_name(0) == "Inicial"
    assert registry.index_to_class_name(1) == "En Desarrollo"
    assert registry.index_to_class_name(2) == "Definido"
    assert registry.index_to_class_name(3) == "Optimizado"


def test_index_to_class_name_raises_key_error_for_out_of_range_index(
    test_artifacts_dir: Path,
) -> None:
    """index_to_class_name raises KeyError for an index outside 0-3."""
    registry = load_all_artifacts(test_artifacts_dir)

    with pytest.raises(KeyError):
        registry.index_to_class_name(99)


def test_missing_model_metadata_falls_back_to_unknown_version(
    build_artifacts_dir: Callable[..., Path],
) -> None:
    """A missing model_metadata.json does not raise; model_version falls back to 'unknown'."""
    directory = build_artifacts_dir(exclude=frozenset({"model_metadata.json"}))

    registry = load_all_artifacts(directory)

    assert registry.model_version == "unknown"
