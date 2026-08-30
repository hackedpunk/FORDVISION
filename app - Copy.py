
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI(title="FordVision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "fordvision_deployment_champion.joblib"

artifact = joblib.load(MODEL_PATH)

if isinstance(artifact, dict):
    model = artifact.get("model", artifact)
else:
    model = artifact


class CarData(BaseModel):
    model: str
    year: int
    transmission: str
    mileage: int
    fuelType: str
    tax: int
    mpg: float
    engineSize: float


FEATURE_COLUMNS = [
    "model",
    "year",
    "transmission",
    "mileage",
    "fuelType",
    "tax",
    "mpg",
    "engineSize",
    "car_age",
    "mileage_per_year",
]


@app.get("/")
def home():
    return {
        "service": "FordVision",
        "status": "running",
        "model": "fordvision_deployment_champion",
        "verified_r2_percent": 96.7219651082,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
    }


@app.post("/predict")
def predict(car: CarData):

    data = car.model_dump()

    CURRENT_YEAR = 2026

    car_age = CURRENT_YEAR - data["year"]

    mileage_per_year = (
        data["mileage"] / max(car_age, 1)
    )

    data["car_age"] = car_age
    data["mileage_per_year"] = mileage_per_year

    input_data = pd.DataFrame(
        [data]
    )[FEATURE_COLUMNS]

    # IMPORTANT:
    # Do NOT pass cat_features to predict().
    prediction = float(
        model.predict(input_data)[0]
    )

    # Real CatBoost SHAP values
    shap_matrix = model.get_feature_importance(
        data=input_data,
        type="ShapValues"
    )

    shap_row = shap_matrix[0]

    shap_contributions = shap_row[:-1]

    base_value = float(
        shap_row[-1]
    )

    shap_values = [
        {
            "feature": feature,
            "impact": round(float(impact), 2)
        }
        for feature, impact in zip(
            FEATURE_COLUMNS,
            shap_contributions
        )
    ]

    shap_values.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True
    )

    return {
        "predicted_price": round(
            prediction, 2
        ),

        "base_value": round(
            base_value, 2
        ),

        "shap_values": shap_values,

        "model_r2_percent": 96.7219651082
    }

