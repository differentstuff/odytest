@echo off
:: OdyTest - Model Evaluation Suite Setup Script
:: Creates virtual environment and installs dependencies

echo.
echo ========================================
echo  OdyTest - Model Evaluation Suite Setup
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
)

echo Python found:
python --version
echo.

:: Check if we're in the correct directory
if not exist "config.py" (
    echo ERROR: Please run this script from the tests/odytest directory
    echo Current directory should contain config.py
    pause
)

:: Create virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
)

echo Virtual environment created successfully.
echo.

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
)

echo Virtual environment activated.
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo.

:: Install requi::ents
echo Installing requi::ents...
pip install -r requi::ents.txt
if errorlevel 1 (
    echo ERROR: Failed to install requi::ents
    echo Please check requi::ents.txt and try again
    pause
)

echo.
echo ========================================
echo  Setup completed successfully!
echo ========================================
echo.
echo Virtual environment is ready at: %CD%\venv
echo.
echo To activate the environment manually:
echo   venv\Scripts\activate.bat
echo.
echo To run OdyTest:
echo   run.bat
echo.
echo To test the installation:
echo   python demo.py
echo.
echo ========================================

pause
