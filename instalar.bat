@echo off
title Instalador - Reconocedor de caras
cd /d "%~dp0"
echo.
echo Instalando Reconocedor de caras...
echo Este proceso puede tardar varios minutos.
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python no esta instalado.
  echo Descarga Python 3.10 o superior desde https://www.python.org/downloads/
  pause
  exit /b 1
)
py -m venv .venv
if errorlevel 1 goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -e .
if errorlevel 1 goto :error
faceguard download-models
if errorlevel 1 goto :error
echo.
echo INSTALACION COMPLETADA.
echo Ahora haz doble clic en iniciar.bat
pause
exit /b 0

:error
echo.
echo La instalacion no pudo completarse. Revisa el mensaje anterior.
pause
exit /b 1


