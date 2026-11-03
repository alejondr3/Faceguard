@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo El programa todavia no esta instalado.
  echo Ejecuta instalar.bat primero.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" -m faceguard.gui
exit /b 0


