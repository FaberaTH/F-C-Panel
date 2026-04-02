@echo off
setlocal
cd /d %~dp0

echo [1/2] Verificando executavel...
if not exist dist\PainelFS2024-Configurator.exe (
  echo Executavel nao encontrado. Rode build_exe.bat primeiro.
  pause
  exit /b 1
)

echo [2/2] Gerando instalador com Inno Setup...
if not defined ISCC_PATH set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%ISCC_PATH%" (
  echo ISCC nao encontrado em: %ISCC_PATH%
  echo Instale o Inno Setup 6 e ajuste a variavel ISCC_PATH neste arquivo.
  pause
  exit /b 1
)

"%ISCC_PATH%" installer\PainelFS2024Configurator.iss

echo Instalador gerado em software\bridge-msfs\dist\
pause
endlocal
