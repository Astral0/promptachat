@echo off
title PromptAchat - Resolution Automatique
echo [RESOLUTION] PromptAchat - Resolution automatique des problemes
echo ========================================================
echo.

echo [ETAPE 1] Verification de l'environnement conda...
call conda activate promptachat
if errorlevel 1 (
    echo [ERREUR] Environnement conda 'promptachat' non trouve
    echo [INFO] Impossible de continuer sans l'environnement conda
    echo [ACTION] Executez d'abord : conda create -n promptachat python=3.11 nodejs=18
    pause
    exit /b 1
)

echo [OK] Environnement conda active
echo.

echo [ETAPE 2] Installation de SQLAlchemy...
python -c "import sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation de SQLAlchemy en cours...
    pip install sqlalchemy
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation de SQLAlchemy
    ) else (
        echo [OK] SQLAlchemy installe avec succes
    )
) else (
    echo [OK] SQLAlchemy deja installe
)

echo.
echo [ETAPE 3] Verification et installation de Node.js/npm...
where npm >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation de Node.js et npm...
    conda install nodejs npm -c conda-forge -y
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation de Node.js/npm
    ) else (
        echo [OK] Node.js et npm installes avec succes
    )
) else (
    echo [OK] Node.js et npm deja installes
)

echo.
echo [ETAPE 4] Installation des dependances frontend...
if exist "..\frontend\node_modules" (
    echo [OK] Dependances frontend deja installees
) else (
    echo [INFO] Installation des dependances frontend...
    cd ..\frontend
    npm install
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances frontend
        cd ..\windows
    ) else (
        echo [OK] Dependances frontend installees avec succes
        cd ..\windows
    )
)

echo.
echo [ETAPE 5] Creation des repertoires necessaires...
if not exist "..\backend\uploaded_files" (
    echo [INFO] Creation du repertoire backend\uploaded_files...
    mkdir ..\backend\uploaded_files
    echo [OK] Repertoire cree
) else (
    echo [OK] Repertoire backend\uploaded_files existe deja
)

echo.
echo [ETAPE 6] Verification de la configuration...
if not exist "..\config.ini" (
    if exist "..\config.ini.template" (
        echo [INFO] Creation du fichier config.ini depuis le template...
        copy ..\config.ini.template ..\config.ini
        echo [OK] Fichier config.ini cree
    ) else (
        echo [ERREUR] Template config.ini.template non trouve
    )
) else (
    echo [OK] Fichier config.ini existe deja
)

echo.
echo [ETAPE 7] Verification des ports...
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 3000 occupe - vous devrez peut-etre fermer l'application qui l'utilise
)

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 8001 occupe - vous devrez peut-etre fermer l'application qui l'utilise
)

echo.
echo [ETAPE 8] Test final des dependances...
echo [INFO] Test des dependances Python...
python -c "import fastapi, uvicorn, sqlalchemy; print('[OK] Toutes les dependances Python sont disponibles')" 2>nul || echo "[ERREUR] Certaines dependances Python manquent encore"

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] npm toujours non disponible
) else (
    echo [OK] npm disponible
)

echo.
echo ========================================
echo [TERMINE] Resolution terminee !
echo ========================================
echo.
echo [RESULTAT] Verification finale...
call check_installation.bat 