# Ítaca SmartDiag

Sistema de autodiagnóstico empresarial con Deep Learning — Proyecto Capstone, Samsung Innovation Campus (AI Course).

## Descripción

Ítaca, empresa de consultoría, necesita escalar su capacidad de diagnóstico sin aumentar proporcionalmente su equipo humano. Este sistema automatiza la primera fase del ciclo de consultoría: el cliente diligencia un formulario web, una red neuronal profunda (DNN) multimodal clasifica el nivel de madurez de su negocio (Inicial, En Desarrollo, Definido, Optimizado) y un motor de recomendaciones entrega una acción concreta según su sector. Opcionalmente, una capa de personalización con LLM (Claude Haiku) adapta la redacción de la recomendación al texto libre del cliente.

## Arquitectura

- **Modelo:** DNN multimodal en TensorFlow/Keras — rama tabular (10 features: numéricas escaladas + categóricas one-hot) + rama NLP (`TextVectorization` + `Embedding` + `GlobalAveragePooling1D`) sobre la respuesta en texto libre del cliente, con fusión tardía antes de la cabeza de clasificación.
- **Backend:** FastAPI, arquitectura modular por capas (`core`, `models`, `schemas`, `services`, `routers`, `utils`), SQLAlchemy (SQLite en desarrollo local, PostgreSQL en despliegue).
- **Frontend:** React 18 + Vite + TailwindCSS — SPA de tres vistas (formulario → carga → dashboard de resultados).

## Estado actual del modelo

Entrenado y evaluado sobre el conjunto de test (300 muestras, split 75/15/10):

- **Accuracy:** 1.0000 · **F1 macro:** 1.0000
- **Estudio de ablación:** tabular-solo F1=0.9971, NLP-solo F1=1.0000, multimodal F1=1.0000 — confirma que la señal tabular es dominante y la rama de texto aporta la fracción final.
- **Prueba de robustez OOV:** con texto forzado fuera de vocabulario, accuracy cae de 1.00 a 0.76 — limitación conocida y documentada, mitigada por la capa de personalización LLM.
- Métricas altas por naturaleza del dataset sintético (ver `HALLAZGO_Conflicto_Texto_Tabular.md` para el análisis honesto de esta limitación).

## Datos

Dataset de 3000 diagnósticos históricos provistos por Ítaca (`diagnosticos_itaca.csv`): sector, tamaño de empresa, porcentaje de procesos documentados, presupuesto anual de tecnología, respuesta en texto libre, nivel de madurez (objetivo) y recomendación principal.

## Estructura del proyecto

```
.
├── ETL/
│   └── EtL_Stage1.ipynb          # ETL Stage 1 + EDA (limpieza y análisis)
├── data/
│   ├── diagnosticos_itaca.csv           # dataset original
│   ├── diagnosticos_itaca_clean.csv     # dataset limpio (UTF-8)
│   └── catalogo_recomendaciones.csv     # catálogo del motor de recomendaciones
├── preprocessing/                # splits, scaler, encoder, vocab, tensores (Semana 1)
├── training/                     # notebook de entrenamiento, ablación, métricas
├── model/                        # artefactos de entrenamiento (checkpoints, curvas, metadata)
├── app/                          # backend FastAPI
│   ├── core/                     # config.py, logging.py
│   ├── models/                   # diagnostic.py (ORM)
│   ├── schemas/                  # request.py, response.py (Pydantic)
│   ├── services/                 # inference, recommendation, personalization, orchestrator
│   ├── routers/                  # diagnostico.py, health.py, state.py
│   ├── utils/                    # artifact_loader.py
│   └── main.py                   # entry point (FastAPI + lifespan)
├── artifacts/                    # artefactos de runtime (ver tabla abajo)
├── frontend/                     # aplicación React + Vite + Tailwind
├── tests/                        # suite de pytest
├── requirements.txt
└── README.md
```

### Artefactos de runtime (`artifacts/`)

Copiados desde Google Drive tras el entrenamiento en Colab. Son los únicos archivos que el backend necesita para servir inferencias — el resto del material de entrenamiento (checkpoints, curvas, historial) queda en `model/` como respaldo para el informe.

| Archivo | Origen | Uso |
|---|---|---|
| `itaca_serving.keras` | Entrenamiento | Modelo con vectorización de texto embebida; recibe tabular + texto crudo |
| `scaler.joblib` | Preprocessing (Tarea A) | Escala las 2 variables numéricas |
| `onehot_encoder.joblib` | Preprocessing (Tarea A) | Codifica sector / tamaño de empresa |
| `class_map.json` | Preprocessing (Tarea A) | Mapeo nombre de clase ↔ índice |
| `class_weights.json` | Preprocessing (Tarea A) | Pesos de clase usados en entrenamiento (no se usa en runtime) |
| `catalogo_recomendaciones.csv` | ETL Stage 1 | Motor de recomendaciones (16 combinaciones sector × nivel) |
| `model_metadata.json` | Entrenamiento | Versión del modelo, hiperparámetros, métricas — trazabilidad en las respuestas de la API |

## Uso rápido

### ETL + EDA

```bash
python ETL/EtL_Stage1.ipynb   # o su versión .py exportada
```

### Backend

```bash
python -m venv itaca
source itaca/bin/activate        # Windows: itaca\Scripts\activate
pip install -r requirements.txt

# copiar los 7 artefactos de la tabla anterior en artifacts/
# crear .env con ANTHROPIC_API_KEY si se activa la personalización (Camino 2)

uvicorn app.main:app --reload --port 8005
```

Documentación interactiva: `http://localhost:8005/docs`

### Tests

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Stack y versiones clave

Fijadas para que coincidan exactamente con el entorno de entrenamiento en Colab (ver `requirements.txt` para la lista completa y comentarios de compatibilidad):

- Python 3.13
- TensorFlow-CPU 2.20.0 / Keras 3.13.2
- NumPy 2.1.3 / scikit-learn 1.9.0
- FastAPI + SQLAlchemy 2.0
- React 18 + Vite + TailwindCSS 3.4.7

## Cronograma

| Semana | Entregable |
| -------- | ------------ |
| 1 | ETL + EDA, preprocesamiento (splits, scaler, encoder, vocabulario), arquitectura del modelo |
| 2 | Entrenamiento DNN, evaluación, ablación, backend FastAPI (core, servicios, routers) |
| 3 | Frontend React, integración end-to-end, tests, informe final |

## Equipo

Proyecto desarrollado por el equipo **SageSpark** — Samsung Innovation Campus 2026.
