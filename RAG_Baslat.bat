@echo off
title RAG Sistemi Baslatici
color 0A

:: Bulunulan klasore gec
cd /d "%~dp0"

:: 1. Python Kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [HATA] Sistemde Python bulunamadi!
    echo Lutfen Python 3.10+ kurun ve 'Add Python to PATH' secenegini isaretleyin.
    pause
    exit /b
)

:: 2. Kutuphane Yukleme
echo [1/4] Gerekli Python kutuphaneleri kontrol ediliyor...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0E
    echo [UYARI] Bazi paketler yuklenemedi veya zaten yuklu. Calismaya devam ediliyor...
)

:: 3. Foundry Sunucusu
echo [2/4] Microsoft Foundry sunucusu baslatiliyor (Port: 50000)...
start "Foundry Server" powershell -NoExit -Command "foundry server start --port 50000"

:: Sunucunun ayaga kalkmasi icin 4 saniye bekle
timeout /t 4 /nobreak >nul

:: 4. Modelleri Bellege Yukleme
echo [3/4] Modeller yukleniyor...
start "Model Yukleyici" powershell -NoExit -Command "Write-Host 'Modeller yukleniyor, lutfen bekleyin...'; foundry model load; foundry model load"

:: Modellerin bellege oturmasi icin 3 saniye bekle
timeout /t 3 /nobreak >nul

:: 5. Streamlit Arayuzu
echo [4/4] Streamlit arayuzu baslatiliyor...
start "Streamlit App" cmd /k "python -m streamlit run app.py"

echo.
echo ========================================================
echo RAG Asistani baslatildi! Tarayici penceresi acilacaktir.
echo ========================================================
timeout /t 3 >nul
exit
