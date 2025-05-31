@echo off
title PromptAchat - Correction npm
echo [CORRECTION] PromptAchat - Correction du probleme npm
echo ===============================================
echo.

echo [ETAPE 1] Activation de l'environnement conda...
call conda activate promptachat
if errorlevel 1 (
    echo [ERREUR] Environnement conda 'promptachat' non trouve
    echo [SOLUTION] Creez l'environnement d'abord avec : conda create -n promptachat python=3.11
    pause
    exit /b 1
)

echo [OK] Environnement conda active
echo.

echo [ETAPE 2] Verification de l'installation actuelle...
where node >nul 2>&1
if not errorlevel 1 (
    echo [OK] Node.js trouve : 
    node --version
) else (
    echo [ERREUR] Node.js non trouve dans l'environnement conda
)

where npm >nul 2>&1
if not errorlevel 1 (
    echo [OK] npm trouve : 
    npm --version
) else (
    echo [ERREUR] npm non trouve dans l'environnement conda
)

echo.
echo [ETAPE 3] Installation de Node.js dans l'environnement conda...
conda install nodejs npm -c conda-forge -y

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'installation de Node.js
    echo [SOLUTION] Essayez manuellement : conda install nodejs npm -c conda-forge
    pause
    exit /b 1
)

echo [OK] Node.js et npm installes avec succes !
echo.

echo [ETAPE 4] Verification post-installation...
call conda activate promptachat
where node
where npm
node --version
npm --version

echo.
echo [TERMINE] Correction terminee !
echo [ACTION] Vous pouvez maintenant relancer : start_promptachat_manual.bat
echo.
pause 