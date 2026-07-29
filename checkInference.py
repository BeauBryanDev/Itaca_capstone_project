import joblib

scaler = joblib.load("artifacts/scaler.joblib")
encoder = joblib.load("artifacts/onehot_encoder.joblib")

print("scaler.feature_names_in_:", getattr(scaler, "feature_names_in_", "NO DISPONIBLE"))
print("scaler.mean_:", scaler.mean_)
print("scaler.scale_:", scaler.scale_)
print()
print("encoder.feature_names_in_:", getattr(encoder, "feature_names_in_", "NO DISPONIBLE"))
print("encoder.categories_:", encoder.categories_)



