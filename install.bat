@echo off
setlocal
cd /d "%~dp0"
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Optional AI backends can be installed with:
echo pip install -r requirements-ai.txt
pause
