@echo off
REM Gera o executavel unico do Extrator de Desenhos (rodar na maquina Windows)
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name "ExtratorDesenhosLS" main.py
echo.
echo Executavel gerado em: dist\ExtratorDesenhosLS.exe
pause
