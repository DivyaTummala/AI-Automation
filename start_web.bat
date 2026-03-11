@echo off
echo ============================================================
echo Starting ETL - Validation testing (Web Interface)
echo ============================================================
echo.
echo The application will be available at:
echo.
echo    http://localhost:3000
echo    http://127.0.0.1:3000
echo    http://10.10.32.214:3000
echo.
echo ============================================================
echo.
cd /d "%~dp0"
python app.py
pause

