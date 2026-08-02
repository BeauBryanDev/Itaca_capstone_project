# Backend test suite

## Running the suite

```bash
pip install -r requirements.txt
pytest
```

Everything runs offline: no test calls the Anthropic API, loads the real
trained model, or touches a real database. The full suite finishes in a
few seconds.

To run a single file or test:

```bash
pytest tests/test_router_diagnostico.py
pytest tests/test_router_diagnostico.py::test_get_diagnostico_with_unknown_id_returns_404
```

## How the fixture artifacts are built

`tests/conftest.py` builds a minimal but structurally valid artifacts
directory instead of depending on the real, multi-hundred-KB model
downloaded from Google Drive:

- **`itaca_serving.keras`**: a tiny multimodal Keras model built once per
  test session (`shared_serving_model_path`) and copied into each test's
  own directory. It matches the real serving model's input/output
  contract exactly (`tabular_input` shape `(10,)`, `text_input` shape
  `(1,)` string, 4-class softmax output) but has random, untrained
  weights, since these tests verify plumbing (shapes, wiring, error
  handling), not predictive accuracy, which is validated separately in
  `training/Itaca_model_training.ipynb` and `training/metrics_report.json`.
- **`scaler.joblib` / `onehot_encoder.joblib`**: a `StandardScaler` and
  `OneHotEncoder` fitted on a few rows of representative dummy data,
  covering every real sector and company size.
- **`class_map.json`**: the real four-class mapping the whole system
  depends on.
- **`catalogo_recomendaciones.csv`**: all 16 `(sector, maturity_level)`
  combinations, so a fixture-model prediction always resolves to a
  recommendation regardless of which class it lands on.
- **`model_metadata.json`**: a fixed `model_name` (`itaca-fixture-model`)
  that router tests assert against.

`build_artifacts_dir` is a factory fixture: call it with
`exclude={"scaler.joblib"}` (or any other artifact file name) to build a
directory missing one file, for testing the artifact loader's failure
paths.

`app_env` points the application's settings (`ARTIFACTS_DIR`,
`DATABASE_URL`) at fixture artifacts and an isolated on-disk SQLite file
per test, and clears the `get_settings()` cache before and after so tests
never leak configuration into each other. `client` builds a `TestClient`
from the real app through its real `lifespan`; `db_engine` opens a second,
independent connection to the same database file so router tests can
verify persistence directly instead of trusting the HTTP response alone.
