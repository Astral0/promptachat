@echo off
title PromptAchat - Liberation des Ports
echo [PORTS] PromptAchat - Liberation des ports 3000 et 8001
echo =====================================================
echo.

echo [INFO] Recherche des processus utilisant les ports 3000 et 8001...
echo.

echo [PORT 3000] Verification du port 3000...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :3000') do (
    if not "%%i"=="0" (
        echo [TROUVE] Processus %%i utilise le port 3000
        echo [ACTION] Arret du processus %%i...
        taskkill /F /PID %%i >nul 2>&1
        if errorlevel 1 (
            echo [ERREUR] Impossible d'arreter le processus %%i
        ) else (
            echo [OK] Processus %%i arrete
        )
    )
)

echo.
echo [PORT 8001] Verification du port 8001...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8001') do (
    if not "%%i"=="0" (
        echo [TROUVE] Processus %%i utilise le port 8001
        echo [ACTION] Arret du processus %%i...
        taskkill /F /PID %%i >nul 2>&1
        if errorlevel 1 (
            echo [ERREUR] Impossible d'arreter le processus %%i
        ) else (
            echo [OK] Processus %%i arrete
        )
    )
)

echo.
echo [VERIFICATION] Verification finale des ports...
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 3000 encore occupe
) else (
    echo [OK] Port 3000 libre
)

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [ATTENTION] Port 8001 encore occupe
) else (
    echo [OK] Port 8001 libre
)

echo.
echo [TERMINE] Liberation des ports terminee !
echo [INFO] Vous pouvez maintenant lancer start_promptachat_manual.bat
echo.
pause 