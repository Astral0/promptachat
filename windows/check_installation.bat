@echo off
title PromptAchat - Verification Installation
echo [DIAGNOSTIC] PromptAchat - Verification de l'Installation
echo ===============================================
echo.

echo [1/8] Verification de l'environnement conda...
call conda activate promptachat
if errorlevel 1 (
    echo [ERREUR] Environnement conda 'promptachat' non trouve
    echo [SOLUTION] Creez-le avec : conda create -n promptachat python=3.11 nodejs=18
    echo.
    goto :check_files
) else (
    echo [OK] Environnement conda 'promptachat' active
)

echo.
echo [2/8] Verification de Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non trouve
) else (
    echo [OK] Python trouve : 
    python --version
)

echo.
echo [3/8] Verification de Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js non trouve
    echo [SOLUTION] Installez avec : conda install nodejs npm -c conda-forge
) else (
    echo [OK] Node.js trouve : 
    node --version
)

echo.
echo [4/8] Verification de npm...
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] npm non trouve
    echo [SOLUTION] Installez avec : conda install nodejs npm -c conda-forge
) else (
    echo [OK] npm trouve : 
    npm --version
)

:check_files
echo.
echo [5/8] Verification des fichiers du projet...

if exist "..\config.ini" (
    echo [OK] config.ini trouve
) else (
    if exist "..\config.ini.template" (
        echo [ATTENTION] config.ini manquant, mais template trouve
        echo [SOLUTION] Copiez avec : copy ..\config.ini.template ..\config.ini
    ) else (
        echo [ERREUR] config.ini et template manquants
    )
)

if exist "..\backend\server.py" (
    echo [OK] backend\server.py trouve
) else (
    echo [ERREUR] backend\server.py manquant
)

if exist "..\frontend\package.json" (
    echo [OK] frontend\package.json trouve
) else (
    echo [ERREUR] frontend\package.json manquant
)

if exist "..\backend\uploaded_files" (
    echo [OK] Repertoire backend\uploaded_files trouve
) else (
    echo [ATTENTION] Repertoire backend\uploaded_files manquant
    echo [SOLUTION] Creez-le avec : mkdir ..\backend\uploaded_files
)

echo.
echo [6/8] Test des dependances Python...
call conda activate promptachat >nul 2>&1
python -c "import fastapi; print('[OK] FastAPI disponible')" 2>nul || echo "[ERREUR] FastAPI manquant - pip install fastapi"
python -c "import uvicorn; print('[OK] Uvicorn disponible')" 2>nul || echo "[ERREUR] Uvicorn manquant - pip install uvicorn"
python -c "import sqlalchemy; print('[OK] SQLAlchemy disponible')" 2>nul || echo "[ERREUR] SQLAlchemy manquant - pip install sqlalchemy"

echo.
echo [7/8] Test des dependances frontend...
if exist "..\frontend\node_modules" (
    echo [OK] node_modules trouve
) else (
    echo [ERREUR] node_modules manquant
    echo [SOLUTION] Installez avec : cd ..\frontend ^&^& npm install
)

echo.
echo [8/8] Verification des ports...
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 3000 deja utilise
) else (
    echo [OK] Port 3000 libre
)

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 8001 deja utilise
) else (
    echo [OK] Port 8001 libre
)

echo.
echo ========================================
echo RESUME ET RECOMMANDATIONS :
echo ========================================
echo.

call conda activate promptachat >nul 2>&1
if errorlevel 1 (
    echo [CRITIQUE] Environnement conda manquant
    echo [SOLUTION] conda create -n promptachat python=3.11 nodejs=18 -y
    echo.
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [PROBLEME] npm manquant
    echo [SOLUTION] Executez fix_npm_issue.bat
    echo.
)

python -c "import sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo [PROBLEME] SQLAlchemy manquant
    echo [SOLUTION] pip install sqlalchemy
    echo.
)

if not exist "..\config.ini" (
    echo [PROBLEME] Configuration manquante
    echo [SOLUTION] copy ..\config.ini.template ..\config.ini
    echo.
)

if not exist "..\frontend\node_modules" (
    echo [PROBLEME] Dependances frontend manquantes
    echo [SOLUTION] cd ..\frontend ^&^& npm install
    echo.
)

netstat -an | findstr ":3000\|:8001" >nul 2>&1
if not errorlevel 1 (
    echo [PROBLEME] Ports 3000 ou 8001 occupes
    echo [SOLUTION] Fermez les applications qui utilisent ces ports
    echo [INFO] Utilisez : netstat -ano ^| findstr :3000
    echo.
)

echo [TERMINE] Verification terminee !
echo [ACTION] Corrigez les problemes identifies puis relancez start_promptachat_manual.bat
echo.
pause 