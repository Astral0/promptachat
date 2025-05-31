@echo off
title PromptAchat - Demarrage Manuel
echo [DEMARRAGE] PromptAchat - Demarrage Manuel
echo ===============================
echo.

echo [ETAPE 1] Verification de l'environnement...
call conda activate promptachat
if errorlevel 1 (
    echo [ERREUR] Environnement conda 'promptachat' non trouve
    echo [SOLUTION] Executez d'abord : conda create -n promptachat python=3.11 nodejs=18
    pause
    exit /b 1
)

echo [OK] Environnement conda active
echo.

echo [ETAPE 2] Verification des dependances...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non trouve dans l'environnement conda
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] npm non trouve dans l'environnement conda
    echo [SOLUTION] Installez Node.js dans conda : conda install nodejs
    pause
    exit /b 1
)

echo [OK] Python et npm trouves
echo.

echo [ETAPE 3] Lancement du backend...
start "PromptAchat Backend" cmd /k "call conda activate promptachat && cd /d %~dp0..\backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

echo [ETAPE 4] Attente du demarrage du backend (10 secondes)...
ping 127.0.0.1 -n 11 > nul

echo [ETAPE 5] Lancement du frontend...
start "PromptAchat Frontend" cmd /k "call conda activate promptachat && cd /d %~dp0..\frontend && set REACT_APP_BACKEND_URL=http://localhost:8001 && npm start"

echo.
echo [SUCCESS] PromptAchat est en cours de demarrage !
echo.
echo [INFO] URLs d'acces :
echo   - Frontend : http://localhost:3000
echo   - Backend  : http://localhost:8001
echo   - API Docs : http://localhost:8001/docs
echo.
echo [CONNEXION] Connexion par defaut :
echo   Utilisateur : admin
echo   Mot de passe : admin
echo.
echo [ATTENTION] Fermez cette fenetre pour arreter les services
pause 
cd ..\\windows
