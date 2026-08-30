from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# FORDVISION API
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "fordvision_deployment_champion.joblib"

app = FastAPI(
    title="FordVision API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD EXACT SAVED DEPLOYMENT ARTIFACT
# ============================================================

try:
    artifact = joblib.load(MODEL_PATH)

    if not isinstance(artifact, dict):
        raise RuntimeError(
            f"Expected dictionary artifact, got {type(artifact)}"
        )

    model = artifact["model"]
    FEATURE_COLUMNS = artifact["feature_columns"]
    CATEGORICAL_FEATURES = artifact["categorical_features"]

    print("=" * 70)
    print("FORDVISION MODEL LOADED")
    print("=" * 70)
    print("Artifact:", MODEL_PATH)
    print("Model:", type(model))
    print("Feature count:", len(FEATURE_COLUMNS))
    print("Features:", FEATURE_COLUMNS)
    print("Categorical:", CATEGORICAL_FEATURES)
    print("=" * 70)

except Exception as e:
    model = None
    FEATURE_COLUMNS = []
    CATEGORICAL_FEATURES = []
    print("MODEL LOAD ERROR:", repr(e))


# ============================================================
# REQUEST SCHEMA
# ============================================================

class CarData(BaseModel):
    model: str
    year: int
    transmission: str
    mileage: int
    fuelType: str
    tax: int
    mpg: float
    engineSize: float


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def home():
    return {
        "service": "FordVision API",
        "status": "running",
        "model_loaded": model is not None
    }


@app.get("/health")
def health():
    return {
        "status": "healthy" if model is not None else "model_error",
        "model_loaded": model is not None,
        "feature_count": len(FEATURE_COLUMNS)
    }


# ============================================================
# EXACT FEATURE ENGINEERING
# ============================================================

def build_features(car: CarData) -> pd.DataFrame:

    current_year = 2026

    year = float(car.year)
    mileage = float(car.mileage)
    tax = float(car.tax)
    mpg = float(car.mpg)
    engine = float(car.engineSize)

    car_age = max(current_year - year, 0)

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

    features = {
        "model": car.model,
        "year": car.year,
        "transmission": car.transmission,
        "mileage": car.mileage,
        "fuelType": car.fuelType,
        "tax": car.tax,
        "mpg": car.mpg,
        "engineSize": car.engineSize,

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

    missing = [
        column
        for column in FEATURE_COLUMNS
        if column not in features
    ]

    if missing:
        raise RuntimeError(
            f"Missing required model features: {missing}"
        )

    # IMPORTANT:
    # Use the exact feature order stored inside the artifact.
    X = pd.DataFrame([
        {column: features[column] for column in FEATURE_COLUMNS}
    ])

    return X


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict(car: CarData):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Deployment model failed to load."
        )

    try:
        X = build_features(car)

        prediction = model.predict(X)

        price = float(prediction[0])

        if not np.isfinite(price):
            raise RuntimeError(
                f"Model returned invalid prediction: {price}"
            )

        return {
            "predicted_price": round(price, 2)
        }

    except Exception as e:

        print("=" * 70)
        print("PREDICTION ERROR")
        print("=" * 70)
        print(repr(e))
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )