@echo off
echo ======================================================================
echo AI Credit Risk Assessment - Backend API (ML Integrated)
echo ======================================================================
echo.

cd /d "%~dp0"

echo Checking if model is trained...
if exist "data\credit_risk_xgboost_v1.pkl" (
    echo ✅ Model found - Starting API with ML predictions
    echo.
    python app_ml_integrated.py
) else (
    echo ⚠️  Model not found!
    echo.
    echo Please train the model first:
    echo   cd ml_models
    echo   python run_training_pipeline.py
    echo.
    echo Or use the original API with mock predictions:
    echo   python app.py
    echo.
    pause
    exit /b 1
)
