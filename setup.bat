@echo off
REM Setup script for PC Training Environment (Windows)
REM Run this script to set up the training environment

echo ================================================
echo   Touchless Video Controller - PC Setup
echo ================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Python found!
python --version
echo.

echo Installing dependencies from requirements_pc.txt...
cd PC-TRAINING
python -m pip install --upgrade pip
python -m pip install -r requirements_pc.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ================================================
echo Setup complete!
echo ================================================
echo.
echo Next steps:
echo 1. Collect training data:
echo    cd PC-TRAINING
echo    python collect_data.py
echo.
echo 2. Train the model:
echo    python train_model.py
echo.
echo 3. Convert to TFLite:
echo    python create_compatible_tflite.py
echo.
echo 4. Transfer files to Jetson Nano:
echo    - gesture_model_v1.tflite
echo    - model_info.json
echo    - media_control_mpv.py
echo.
echo ================================================
pause
