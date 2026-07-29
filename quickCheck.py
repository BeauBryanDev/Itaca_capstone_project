import joblib
import pandas as pd

scaler = joblib.load("artifacts/scaler.joblib")
encoder = joblib.load("artifacts/onehot_encoder.joblib")

# StandardScaler fue ajustado con nombres de columna -> pasar DataFrame
numeric_df = pd.DataFrame(
    [[0.5, 5000000]],
    columns=["porcentaje_procesos_documentados", "presupuesto_anual_tecnologia"],
)
print(scaler.transform(numeric_df))

