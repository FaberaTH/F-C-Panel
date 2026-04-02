@echo off
setlocal
cd /d %~dp0

echo [1/3] Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo [2/3] Gerando executavel...
if exist ..\..\assets\branding\app.ico (
	python -m PyInstaller --noconfirm --onefile --windowed --hidden-import=SimConnect --name PainelFS2024-Configurator --icon ..\..\assets\branding\app.ico app.py
) else (
	python -m PyInstaller --noconfirm --onefile --windowed --hidden-import=SimConnect --name PainelFS2024-Configurator app.py
)

echo [3/3] Build concluido.
echo Executavel em: dist\PainelFS2024-Configurator.exe
pause
endlocal
