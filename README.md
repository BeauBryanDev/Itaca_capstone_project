# Ítaca SmartDiag

Sistema de autodiagnóstico empresarial con Deep Learning — Proyecto Capstone, Samsung Innovation Campus (AI Course).

## Descripción

Ítaca, empresa de consultoría, necesita escalar su capacidad de diagnóstico sin aumentar proporcionalmente su equipo humano. Este sistema automatiza la primera fase del ciclo de consultoría: el cliente diligencia un formulario web, una red neuronal profunda (DNN) multimodal clasifica el nivel de madurez de su negocio (Inicial, En Desarrollo, Definido, Optimizado) y un motor de recomendaciones entrega una acción concreta según su sector.

## Arquitectura

- **Modelo:** DNN multimodal en TensorFlow/Keras — rama tabular (variables numéricas y categóricas) + rama NLP (TextVectorization + Embedding) sobre la respuesta en texto libre del cliente.
- **Backend:** FastAPI + PostgreSQL — endpoint de inferencia y motor de recomendaciones (catálogo sector × nivel).
- **Frontend:** React + TypeScript + Tailwind CSS — formulario de autodiagnóstico y panel de resultados.

## Datos

Dataset de 3000 diagnósticos históricos provistos por Ítaca (`diagnosticos_itaca.csv`): sector, tamaño de empresa, porcentaje de procesos documentados, presupuesto anual de tecnología, respuesta en texto libre, nivel de madurez (objetivo) y recomendación principal.

## Estructura del proyecto

```
.
├── etl/
│   └── etl_stage1_eda.py        # ETL Stage 1 + EDA (limpieza y análisis)
├── data/
│   ├── diagnosticos_itaca.csv           # dataset original
│   ├── diagnosticos_itaca_clean.csv     # dataset limpio (UTF-8)
│   └── catalogo_recomendaciones.csv     # catálogo del motor de recomendaciones
├── model/                        # entrenamiento y evaluación (Stage 2-3)
├── backend/                      # API FastAPI
└── frontend/                     # aplicación React
```

## Uso rápido

```bash
# ETL + EDA (genera el dataset limpio y el catálogo de recomendaciones)
python etl/etl_stage1_eda.py
```

Requisitos: Python 3.10+, pandas, numpy. Para el entrenamiento (etapas siguientes): TensorFlow/Keras.

## Cronograma

| Semana | Entregable |
|--------|------------|
| 1 | ETL + EDA, arquitectura del modelo |
| 2 | Entrenamiento DNN, evaluación, backend FastAPI |
| 3 | Frontend React, integración end-to-end, informe final |

## Equipo

Proyecto desarrollado por el equipo **SageSpark** — Samsung Innovation Campus 2026.
