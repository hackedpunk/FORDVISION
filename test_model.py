import joblib

MODEL_PATH = "fordvision_deployment_champion.joblib"

print("=" * 60)
print("FORDVISION — MODEL LOAD TEST")
print("=" * 60)

print("Loading:", MODEL_PATH)

model = joblib.load(MODEL_PATH)

print("SUCCESS")
print("Model type:", type(model))

print("=" * 60)