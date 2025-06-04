@echo off
setlocal enabledelayedexpansion
:: OdyTest - Model Evaluation Suite Runner
:: Activates virtual environment and provides easy access to testing commands

echo.
echo ========================================
echo  OdyTest - Model Evaluation Suite
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first to create the environment
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

:: Check if no arguments provided - show menu
if "%~1"=="" goto :show_menu

:: Handle command line arguments
if /i "%~1"=="demo" goto :run_demo
if /i "%~1"=="list-models" goto :list_models
if /i "%~1"=="list-prompts" goto :list_prompts
if /i "%~1"=="test" goto :run_test
if /i "%~1"=="sequential" goto :run_sequential
if /i "%~1"=="report" goto :generate_report
if /i "%~1"=="help" goto :show_help

echo ERROR: Unknown command "%~1"
echo Run "run.bat help" for available commands
pause
exit /b 1

:show_menu
echo Available Commands:
echo.
echo 1. Demo - Show OdyTest capabilities
echo 2. List Models - Show available models
echo 3. List Prompts - Show available prompt variants
echo 4. Test Single Model - Test one specific model
echo 5. Sequential Tests - Run all models sequentially
echo 6. Generate Report - Create comparative analysis
echo 7. Help - Show detailed command help
echo 0. Exit
echo.
set choice=""
set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto :run_demo
if "%choice%"=="2" goto :list_models
if "%choice%"=="3" goto :list_prompts
if "%choice%"=="4" goto :run_test
if "%choice%"=="5" goto :run_sequential
if "%choice%"=="6" goto :generate_report
if "%choice%"=="7" goto :show_help
if "%choice%"=="0" goto :exit
echo Invalid choice. Please enter 0-7.
echo.
goto :show_menu

:run_demo
echo.
echo Running OdyTest demonstration...
echo ========================================
python demo.py
echo.
pause
goto :show_menu

:list_models
echo.
echo Available Models:
echo ========================================
python test_single_model.py --list-models
echo.
pause
goto :show_menu

:list_prompts
echo.
echo Available Prompt Variants:
echo ========================================
python test_single_model.py --list-prompts
echo.
pause
goto :show_menu

:run_test
echo.
echo Single Model Testing
echo ========================================
echo.
:: Check if we have command line arguments (called with run.bat test model_name)
if not "%~2"=="" (
    :: Called from command line with arguments
    if "%~3"=="" (
        python test_single_model.py %~2
    ) else (
        python test_single_model.py %~2 --prompt %~3
    )
) else (
    :: Called from menu or without arguments - interactive mode
    echo Available models:
    python test_single_model.py --list-models
    echo.
    set /p model="Enter model name: "
    set promptvar=
    set /p promptvar="Enter prompt variant (production, multilingual, concise, structured, chain_of_thought) or press Enter for 'production': "
    if "!promptvar!"=="" set promptvar=production
    python test_single_model.py !model! --prompt !promptvar!
)
echo.
pause
goto :show_menu

:run_sequential
echo.
echo Sequential Model Testing
echo ========================================
echo.
echo This will test all models one by one.
echo Make sure you have Ollama running and models available.
echo.
set /p confirm="Continue? (y/N): "
if /i not "%confirm%"=="y" goto :show_menu

if "%~2"=="" (
    set promptvar=
    set /p promptvar="Enter prompt variant (production, multilingual, concise, structured, chain_of_thought) or press Enter for 'production': "
    if "!promptvar!"=="" set promptvar=production
    python run_sequential_tests.py --prompt !promptvar!
) else (
    python run_sequential_tests.py --prompt %~2
)
echo.
pause
goto :show_menu

:generate_report
echo.
echo Generating Comparative Report
echo ========================================
python run_sequential_tests.py --generate-report-only
echo.
pause
goto :show_menu

:show_help
echo.
echo OdyTest Command Line Usage:
echo ========================================
echo.
echo run.bat demo                    - Show demonstration
echo run.bat list-models             - List available models
echo run.bat list-prompts            - List prompt variants
echo run.bat test [model] [prompt]   - Test single model
echo run.bat sequential [prompt]     - Run sequential tests
echo run.bat report                  - Generate comparative report
echo run.bat help                    - Show this help
echo.
echo Examples:
echo   run.bat test qwen3_4b
echo   run.bat test deepseek_r1 multilingual
echo   run.bat sequential production
echo.
echo Interactive Mode:
echo   run.bat                       - Show interactive menu
echo.
echo Direct Python Usage:
echo   python test_single_model.py qwen3_4b --prompt multilingual
echo   python run_sequential_tests.py --models qwen3_4b deepseek_r1
echo.
pause
goto :show_menu

:exit
echo.
echo Deactivating virtual environment...
deactivate
echo OdyTest session ended.
echo.
