@echo off
echo ========================================================
echo Starting VehicleHub Local Server...
echo ========================================================
echo.
echo Your server is starting. Please open your web browser and go to:
echo.
echo     http://localhost:8000
echo.
echo Keep this black window open while you are using the portal!
echo.
python -m http.server 8000
pause
