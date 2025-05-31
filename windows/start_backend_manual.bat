@echo off
echo [BACKEND] Demarrage manuel du backend PromptAchat...
call conda activate promptachat
cd /d "%~dp0..\backend"
echo [INFO] Demarrage du serveur sur http://localhost:8001
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
pause 