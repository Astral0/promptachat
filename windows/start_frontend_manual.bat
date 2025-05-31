@echo off
echo [FRONTEND] Demarrage manuel du frontend PromptAchat...
call conda activate promptachat
if errorlevel 1 (
    echo [ERREUR] Environnement conda 'promptachat' non trouve
    pause
    exit /b 1
)

echo [OK] Environnement conda active

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] npm non trouve dans l'environnement conda
    echo [SOLUTION] Executez d'abord : fix_npm_issue.bat
    pause
    exit /b 1
)

echo [OK] npm trouve
cd /d "%~dp0..\frontend"

rem Configuration de l'URL du backend pour l'environnement local
set REACT_APP_BACKEND_URL=http://localhost:8001
echo [CONFIG] Backend URL: %REACT_APP_BACKEND_URL%

echo [INFO] Demarrage de React sur http://localhost:3000
npm start
pause 
cd ..\\windows
