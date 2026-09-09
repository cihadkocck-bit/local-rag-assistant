@echo off
title RAG Sistemi Baslatici

:: Bulunulan klasore gec (her bilgisayarda otomatik algilar)
cd /d "%~dp0"

:: Gerekli kutuphaneleri kontrol et ve yukle
echo Gerekli Python kutuphaneleri kontrol ediliyor...
pip install -r requirements.txt

:: 1. Foundry Sunucusu
start "Foundry Server" powershell -NoExit -Command "foundry server start --port 50000"

:: 2. Modelleri Bellege Yukleme
start "Model Yukleyici" powershell -NoExit -Command "Write-Host 'Model listesi aciliyor...'; foundry model load; foundry model load"

:: 3. Streamlit Arayuzu
start "Streamlit App" powershell -NoExit -Command "python -m streamlit run app.py"

exit
