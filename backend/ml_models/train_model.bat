@echo off
echo ======================================================================
echo AI Credit Risk Assessment - ML Model Training
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking system requirements...
python system_check.py
if errorlevel 1 (
    echo.
    echo ERROR: System check failed. Please install required packages.
    echo Run: pip install -r ..\requirements.txt
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [2/4] Starting ML Model Training Pipeline
echo ======================================================================
echo This will take approximately 5 minutes...
echo.

python run_training_pipeline.py
if errorlevel 1 (
    echo.
    echo ERROR: Training failed. Check error messages above.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [3/4] Verifying trained model
echo ======================================================================
echo.

if exist "..\data\credit_risk_xgboost_v1.pkl" (
    echo ✅ Model file created successfully
    for %%A in ("..\data\credit_risk_xgboost_v1.pkl") do echo    Size: %%~zA bytes
) else (
    echo ❌ Model file not found!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [4/4] Training Complete!
echo ======================================================================
echo.
echo ✅ ML model is ready to use
echo.
echo Next steps:
echo   1. Start backend:  cd .. ^&^& python app_ml_integrated.py
echo   2. Start frontend: cd ..\..\frontend ^&^& npm start
echo   3. Open browser:   http://localhost:3000
echo.
echo Documentation:
echo   • Quick Start: QUICKSTART.md
echo   • Full Docs:   README.md
echo   • Summary:     ..\..\ML_IMPLEMENTATION_SUMMARY.md
echo.
echo ======================================================================

pause
