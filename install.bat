@echo off
REM ═══════════════════════════════════════════════════════════
REM  NewsApp — install.bat
REM  Entry point for Windows.
REM  Double-click this file to install.
REM ═══════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════
echo   NewsApp Installer
echo ═══════════════════════════════════════════
echo.

SET SCRIPT_DIR=%~dp0

REM ── 1. Find Python 3.9+ ────────────────────────────────────

SET PYTHON=
FOR %%P IN (python3.12 python3.11 python3.10 python3.9 python3 python py) DO (
    IF NOT DEFINED PYTHON (
        WHERE %%P >nul 2>nul
        IF NOT ERRORLEVEL 1 (
            FOR /F "tokens=*" %%V IN ('%%P -c "import sys; print(\"ok\" if sys.version_info>=(3,9) else \"no\")" 2^>nul') DO (
                IF "%%V"=="ok" SET PYTHON=%%P
            )
        )
    )
)

IF NOT DEFINED PYTHON (
    echo.
    echo   Python 3.9+ not found on PATH.
    echo.
    echo   Please install Python from https://python.org
    echo   Make sure to check "Add Python to PATH" during installation.
    echo   Then re-run install.bat.
    echo.
    pause
    exit /b 1
)

FOR /F "tokens=*" %%V IN ('%PYTHON% --version 2^>^&1') DO echo   Using: %%V

REM ── 2. Hand off to the Python installer ────────────────────

echo.
echo   Handing off to installer\install.py ...
echo.

%PYTHON% "%SCRIPT_DIR%installer\install.py"

IF ERRORLEVEL 1 (
    echo.
    echo   Installation encountered an error.
    pause
    exit /b 1
)

pause
