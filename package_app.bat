@echo off
echo ===== OpenRecall Packaging Script =====
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and try again.
    exit /b 1
)

REM Check if Briefcase is installed
python -m pip show briefcase >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Briefcase...
    python -m pip install briefcase
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install Briefcase.
        exit /b 1
    )
)

REM Create icons
echo Creating application icons...
python create_icons.py
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to create icons. Using default icons.
)

REM Create the application scaffold
echo.
echo Creating application scaffold...
briefcase create
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to create application scaffold.
    exit /b 1
)

REM Build the application
echo.
echo Building application...
briefcase build
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build application.
    exit /b 1
)

REM Package the application
echo.
echo Packaging application as installer...
briefcase package
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to package application.
    exit /b 1
)

echo.
echo ===== Packaging Complete =====
echo The installer can be found in the 'dist' directory.
echo.
