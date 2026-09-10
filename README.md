# FordVision

FordVision is a car-price valuation website powered by a saved CatBoost machine-learning model and a FastAPI backend.

## 1. Requirements

- Windows
- Python 3.x
- VS Code
- Complete FordVision project folder

Example project location:

```text
D:\ford
```

## 2. Open in Visual code studio (VS Code)

### From VS Code
1. Open VS Code.
2. Select **File → Open Folder**.
3. Select the FordVision folder.

### From PowerShell
```powershell
cd D:\ford
code .
```

## 3. Activate the Virtual Environment

If `.venv` is already included:

```powershell
cd D:\ford
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv) PS D:\ford>
```

## 4. Install Dependencies

If `requirements.txt` exists:

```powershell
pip install -r requirements.txt
```

The backend uses packages including FastAPI, Uvicorn, CatBoost, pandas, and joblib.

**Do not retrain the model.** The project uses the saved deployment model.

## 5. Start the ML API

Open the VS Code terminal:

```powershell
cd D:\ford
.\.venv\Scripts\Activate.ps1
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Keep this terminal running.

A successful startup should show:

```text
Uvicorn running on http://127.0.0.1:8000
```

## 6. Verify the API

Open a second terminal and run:

```powershell
curl.exe http://127.0.0.1:8000/health
```

You can also open:

```text
http://127.0.0.1:8000/docs
```

Swagger provides the `POST /predict` endpoint.

## 7. Test a Prediction

Use this PowerShell command:

```powershell
$body = @{
    model = "Fiesta"
    year = 2017
    transmission = "Manual"
    mileage = 30000
    fuelType = "Petrol"
    tax = 150
    mpg = 55.4
    engineSize = 1.0
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/predict" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

This calls the real ML prediction endpoint.

## 8. Start the Frontend

The frontend file is:

```text
index.html
```

For browser-to-API communication, serve it through a local HTTP server instead of opening it directly with `file://`.

Open another terminal:

```powershell
cd D:\ford
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/index.html
```

## 9. Complete Startup

You need two running terminals.

### Terminal 1 — FastAPI / ML backend

```powershell
cd D:\ford
.\.venv\Scripts\Activate.ps1
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend server

```powershell
cd D:\ford
python -m http.server 5500
```

### Browser

```text
http://127.0.0.1:5500/index.html
```

The system works as:

```text
index.html
    |
    | POST /predict
    v
FastAPI
    |
    v
Saved CatBoost Model
    |
    v
Predicted Price
    |
    v
index.html
```

## 10. ML Integration

The website uses the saved CatBoost model through the FastAPI `/predict` endpoint.

The price is **not calculated with a hardcoded frontend formula**.

Do not retrain or replace the model during normal use.

## 11. Verification Test

Use:

```text
Model:          Fiesta
Year:           2017
Transmission:   Manual
Mileage:        30000
Fuel Type:      Petrol
Tax:            150
MPG:            55.4
Engine Size:    1.0
```

The previously verified saved model returned approximately:

```text
£10,810.07
```

## 12. Port 8000 Error

If you see:

```text
[WinError 10048]
only one usage of each socket address...
```

another process is using port 8000.

Check:

```powershell
netstat -ano | findstr :8000
```

If the existing API is already running, **do not start another copy**. Test:

```text
http://127.0.0.1:8000/docs
```

## 13. Website Connection Error

If the website says it cannot connect:

1. Check `http://127.0.0.1:8000/docs`.
2. Check `/health`.
3. Make sure the API terminal is still running.
4. Make sure the frontend server is running on port 5500.
5. Open the website at:

```text
http://127.0.0.1:5500/index.html
```

Do not open it as:

```text
file:///D:/ford/index.html
```

## 14. Recommended Structure

A typical project looks like:

```text
D:\ford
│
├── index.html
├── app.py
├── requirements.txt
├── .venv\
│
├── saved model / deployment files
│
└── other FordVision assets
```

Exact filenames may vary depending on the supplied package.

## 15. Quick Start

After dependencies are installed:

**Terminal 1:**

```powershell
cd D:\ford
.\.venv\Scripts\Activate.ps1
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

**Terminal 2:**

```powershell
cd D:\ford
python -m http.server 5500
```

**Browser:**

```text
http://127.0.0.1:5500/index.html
```

## 16. Troubleshooting Checklist

Check these in order:

1. `.venv` is activated.
2. `app.py` is present.
3. The saved model/deployment file is present.
4. Uvicorn is running on port 8000.
5. `/docs` opens.
6. `/health` reports the model is loaded.
7. `/predict` works from Swagger.
8. The frontend server is running on port 5500.
9. `index.html` is opened through `http://127.0.0.1:5500/`.
10. For frontend errors, use browser Developer Tools → Console/Network.

## 17. Verified Project Status

```text
Real saved ML model       ✅
CatBoost model loaded     ✅
FastAPI backend           ✅
/predict endpoint         ✅
Browser → API request     ✅
Prediction displayed      ✅
Hardcoded price formula   ❌
```

The FordVision ML prediction pipeline is ready for use.
