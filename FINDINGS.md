# Hallazgo — Conflicto de Señal Texto/Tabular en Producción

**Proyecto:** Ítaca SmartDiag — Capstone Samsung Innovation Campus
**Fecha:** Semana 3, pruebas de fuego (fire test) del backend desplegado
**Contexto:** Primeras pruebas manuales de `POST /diagnostico` vía Swagger UI (`/docs`) sobre el backend corriendo en local (puerto 8005), con el modelo `itaca.keras` real y los artefactos de preprocesamiento reales (`scaler.joblib`, `onehot_encoder.joblib`).

---

## 1. Resumen

Durante las primeras pruebas manuales del endpoint `/diagnostico` ya desplegado, se observó que el sistema devolvía consistentemente `"En Desarrollo"` como nivel de madurez, sin importar el valor de `documented_processes_pct` enviado (se probó con 0.08, 0.68 y 0.88). Esto generó una alarma inicial de posible bug crítico en el backend.

La investigación sistemática determinó que **no había ningún error en el modelo, el preprocesamiento ni el backend**. El comportamiento fue una consecuencia esperada y ya anticipada de la arquitectura multimodal: el texto libre enviado en las pruebas era consistente en las tres llamadas y no pertenecía al vocabulario de entrenamiento, y esa señal de texto dominó sobre la señal tabular contradictoria.

## 2. Cronología de la investigación

### Paso 1 — Detección de la anomalía

Tres llamadas consecutivas a `/diagnostico`, variando `documented_processes_pct` (0.08, 0.68, 0.88) y manteniendo fijo el mismo `sector`, `company_size`, `annual_tech_budget` y el mismo `user_response_text`:

> "Tenemos algunos procesos documentados pero nuestra secretaria renunció y nos dejó mucho desorden, yo no entiendo nada."

Resultado en las tres llamadas: `maturity_level = "En Desarrollo"` en todos los casos, con probabilidades que se movían débilmente pero nunca cambiaban la clase predicha — incluso con `documented_processes_pct = 0.88`, donde la regla de bandas del EDA esperaría con altísima probabilidad la clase `"Optimizado"`.

### Paso 2 — Hipótesis descartada: presupuesto extremo

La primera hipótesis fue que un `annual_tech_budget` fuera del rango de entrenamiento (150.000, muy por debajo del rango real de ~3.000.000 a ~261.000.000) estaba causando extrapolación severa en el escalado numérico. Se repitió la prueba con `annual_tech_budget = 3.000.000` (dentro del rango real) y el problema persistió idéntico. Hipótesis descartada.

### Paso 3 — Verificación del pipeline con una fila de entrenamiento conocida

Para aislar si el problema estaba en el backend (orden de columnas, escalado, codificación) o en el modelo, se envió al endpoint una fila real del dataset de entrenamiento (`DIAG_0000`), cuya clase real es `"Inicial"` y que el modelo clasificó con F1=1.0000 durante la evaluación en Colab:

```json
{
  "annual_tech_budget": 3000000,
  "company_size": "Micro",
  "documented_processes_pct": 0.05,
  "sector": "Tecnologia",
  "user_response_text": "El trabajo es muy empírico, no hay documentación de lo que hacemos."
}
```

Resultado: `"Inicial"` con probabilidad **0.9999998**. Esto confirmó que el modelo, el backend, el escalado y la codificación funcionan correctamente. El problema no estaba en el pipeline.

Se verificaron además los artefactos de preprocesamiento directamente (`scaler.feature_names_in_`, `scaler.mean_`, `scaler.scale_`, `encoder.feature_names_in_`, `encoder.categories_`), confirmando que coinciden exactamente con lo esperado del entrenamiento.

### Paso 4 — Identificación de la causa real

Se observó que las tres pruebas del Paso 1 usaban siempre el mismo `user_response_text`, uno que no pertenece a las 32 plantillas del dataset de entrenamiento. Palabras clave de ese texto ("secretaria", "renunció", "desorden", "no entiendo nada") caen mayormente en `[UNK]` (fuera del vocabulario de 108 tokens), pero fragmentos reconocibles como "tenemos algunos procesos documentados" coinciden con el vocabulario asociado a la clase `"En Desarrollo"` en el dataset de entrenamiento.

### Paso 5 — Confirmación final

Se repitió la prueba con `documented_processes_pct = 0.95` (banda de `"Optimizado"`) pero esta vez usando un texto real de esa clase del dataset de entrenamiento:

> "Todo está automatizado, usamos datos para mejorar continuamente."

Resultado: `"Optimizado"` con probabilidad **0.9999967**. Cuando la señal tabular y la señal de texto coinciden, el sistema predice con confianza casi total, igual que en la evaluación de Colab.

## 3. Conclusión

El sistema no tiene ningún defecto. Lo que se observó fue el modelo respondiendo honestamente a una **contradicción real entre las dos modalidades de entrada**:

- Cuando texto y variables tabulares apuntan a la misma clase (como en el dataset de entrenamiento y en las pruebas de los pasos 3 y 5), el modelo predice con confianza cercana al 100%.
- Cuando el texto libre no pertenece al vocabulario de entrenamiento pero contiene fragmentos reconocibles asociados a una clase distinta de la que indican las variables tabulares, la rama NLP puede pesar más que la rama tabular en la predicción final, produciendo una clase distinta a la que la regla de bandas por sí sola indicaría.

Esto es consistente con dos resultados ya medidos durante la evaluación en Colab:

- El estudio de ablación mostró que la variante **"Solo NLP" alcanzó F1 macro = 1.0000** sobre el dataset de test — la rama de texto no es un componente débil o decorativo del modelo; tiene tanto poder predictivo como la rama tabular dentro de la distribución de entrenamiento.
- La prueba de robustez ante texto fuera de vocabulario (texto forzado a `[UNK]` total) mostró una caída de accuracy de 1.00 a 0.76 — una degradación moderada-alta, no despreciable, que ya advertía que el comportamiento del modelo ante texto real y no visto podía ser inestable.

Este hallazgo es la primera observación de ese comportamiento **en el sistema desplegado real**, con texto escrito de forma natural (no un experimento sintético de `[UNK]` total), lo que lo hace más representativo de lo que ocurrirá con clientes reales de Itaca.

## 4. Relevancia para el proyecto

Este hallazgo refuerza, con evidencia empírica de extremo a extremo, la justificación técnica de la arquitectura de personalización con LLM (Camino 2):

- Un cliente real de Itaca escribirá su situación en sus propias palabras, no en una de las 32 plantillas sintéticas del dataset.
- La rama NLP del modelo, entrenada sobre esas 32 plantillas, puede interpretar mal ese texto real y arrastrar la predicción final hacia una clase incorrecta, incluso cuando las variables tabulares (más confiables y menos dependientes del vocabulario) apuntan claramente a la clase correcta.
- La capa de personalización con LLM (Claude Haiku) no solo mejora la redacción de la recomendación: al operar sobre el texto libre completo con comprensión real del español, compensa precisamente la limitación de vocabulario que este hallazgo expone en la rama NLP de la DNN.

## 5. Evidencia (payloads y respuestas completas)

### Caso A — Texto contradictorio, tabular variable (comportamiento inicial observado)

Request (ejemplo con `documented_processes_pct = 0.88`):
```json
{
  "annual_tech_budget": 3000000,
  "company_name": "Textiles del Norte S.A.S.",
  "company_size": "Mediana",
  "documented_processes_pct": 0.88,
  "personalize": false,
  "sector": "Manufactura",
  "user_response_text": "Tenemos algunos procesos documentados pero nuestra secretaria renunció y nos dejó mucho desorden, yo no entiendo nada."
}
```

Response:
```json
{
  "maturity_level": "En Desarrollo",
  "class_probabilities": {
    "Inicial": 0.0163,
    "En Desarrollo": 0.6457,
    "Definido": 0.2336,
    "Optimizado": 0.1044
  }
}
```

### Caso B — Fila real de entrenamiento (DIAG_0000, clase real: Inicial)

Request:
```json
{
  "annual_tech_budget": 3000000,
  "company_size": "Micro",
  "documented_processes_pct": 0.05,
  "sector": "Tecnologia",
  "user_response_text": "El trabajo es muy empírico, no hay documentación de lo que hacemos."
}
```

Response:
```json
{
  "maturity_level": "Inicial",
  "class_probabilities": {
    "Inicial": 0.9999998,
    "En Desarrollo": 0.0000000389,
    "Definido": 0.0000000280,
    "Optimizado": 0.0000001962
  }
}
```

### Caso C — Texto y tabular coherentes en clase Optimizado

Request:
```json
{
  "annual_tech_budget": 200000000,
  "company_size": "Grande",
  "documented_processes_pct": 0.95,
  "sector": "Tecnologia",
  "user_response_text": "Todo está automatizado, usamos datos para mejorar continuamente."
}
```

Response:
```json
{
  "maturity_level": "Optimizado",
  "class_probabilities": {
    "Inicial": 0.0000001,
    "En Desarrollo": 0.0000018,
    "Definido": 0.0000014,
    "Optimizado": 0.9999967
  }
}
```

