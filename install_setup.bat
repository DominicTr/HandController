@echo off
echo ==========================================
echo Installing AI Virtual Mouse Dependencies...
echo ==========================================
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ==========================================
echo Installation Complete! You can close this window.
echo ==========================================
pause