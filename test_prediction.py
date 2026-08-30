import joblib
import pandas as pd
import numpy as np

PATH = r"D:\ford\fordvision_deployment_champion.joblib"

print("=" * 70)
print("FORDVISION — EXACT 20-FEATURE MODEL TEST")
print("=" * 70)

artifact = joblib.load(PATH)

model = artifact["model"]
feature_columns = artifact["feature_columns"]
categorical_features = artifact["categorical_features"]

print("Model:", type(model))
print("Expected feature count:", len(feature_columns))
print("Expected features:")
for i, f in enumerate(feature_columns, 1):
    print(f"{i:2}. {f}")

# ------------------------------------------------------------
# TEST CAR
# ------------------------------------------------------------

car = {
    "model": "Fiesta",
    "year": 2017,
    "transmission": "Manual",
    "mileage": 30000,
    "fuelType": "Petrol",
    "tax": 150,
    "mpg": 55.4,
    "engineSize": 1.0
}

CURRENT_YEAR = 2026

year = float(car["year"])
mileage = float(car["mileage"])
tax = float(car["tax"])
mpg = float(car["mpg"])
engine = float(car["engineSize"])

car_age = max(CURRENT_YEAR - year, 0)

# ------------------------------------------------------------
# ENGINEERED FEATURES
# ------------------------------------------------------------

mileage_per_year = mileage / max(car_age, 1)

mileage_per_age = mileage / max(car_age, 1)

mileage_per_age2 = mileage / max(car_age ** 2, 1)

engine_per_age = engine / max(car_age, 1)

mpg_per_engine = mpg / max(engine, 0.001)

tax_per_engine = tax / max(engine, 0.001)

mileage_engine = mileage * engine

age_sq = car_age ** 2

mileage_log = np.log1p(mileage)

engine_sq = engine ** 2

mpg_sq = mpg ** 2

# ------------------------------------------------------------
# COMPLETE FEATURE DICTIONARY
# ------------------------------------------------------------

features = {
    "model": car["model"],
    "year": car["year"],
    "transmission": car["transmission"],
    "mileage": car["mileage"],
    "fuelType": car["fuelType"],
    "tax": car["tax"],
    "mpg": car["mpg"],
    "engineSize": car["engineSize"],

    "car_age": car_age,
    "mileage_per_year": mileage_per_year,
    "mileage_per_age": mileage_per_age,
    "mileage_per_age2": mileage_per_age2,
    "engine_per_age": engine_per_age,
    "mpg_per_engine": mpg_per_engine,
    "tax_per_engine": tax_per_engine,
    "mileage_engine": mileage_engine,
    "age_sq": age_sq,
    "mileage_log": mileage_log,
    "engine_sq": engine_sq,
    "mpg_sq": mpg_sq
}

# ------------------------------------------------------------
# VERIFY NOTHING IS MISSING
# ------------------------------------------------------------

missing = [f for f in feature_columns if f not in features]

if missing:
    raise RuntimeError(
        "Still missing features: " + str(missing)
    )

# Use EXACT order stored in deployment artifact
X = pd.DataFrame([
    {f: features[f] for f in feature_columns}
])

print("\n" + "=" * 70)
print("MODEL INPUT")
print("=" * 70)

print(X.to_string(index=False))

# ------------------------------------------------------------
# VERIFY CATEGORICAL FEATURES
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CATEGORICAL FEATURES")
print("=" * 70)

for f in categorical_features:
    print(f"{f}: {X[f].iloc[0]!r}")

# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RUNNING SAVED CATBOOST MODEL")
print("=" * 70)

prediction = model.predict(X)

price = float(prediction[0])

print("\n" + "=" * 70)
print("FORDVISION RESULT")
print("=" * 70)

print(f"Predicted price: £{price:,.2f}")

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)
print("20/20 required features supplied.")
print("Saved CatBoost model used.")
print("No hardcoded price calculation used.")
print("=" * 70)
