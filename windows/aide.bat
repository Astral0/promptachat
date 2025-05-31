@echo off
title PromptAchat - Aide
echo [AIDE] PromptAchat - Scripts d'aide disponibles
echo ===============================================
echo.
echo [INFO] Scripts Windows disponibles pour PromptAchat :
echo [LOCATION] Tous les scripts se trouvent dans le repertoire windows/
echo.
echo === DIAGNOSTIC ET RESOLUTION ===
echo.
echo 1. check_installation.bat
echo    [DESC] Diagnostic complet de l'installation
echo    [USAGE] Executez en premier pour identifier les problemes
echo.
echo 2. resoudre_problemes.bat  
echo    [DESC] Resolution automatique des problemes detectes
echo    [USAGE] Executez apres le diagnostic pour corriger automatiquement
echo.
echo 3. fix_npm_issue.bat
echo    [DESC] Corrige specifiquement le probleme npm/Node.js
echo    [USAGE] Si Node.js/npm ne sont pas detectes dans conda
echo.
echo 4. liberer_ports.bat
echo    [DESC] Libere les ports 3000 et 8001
echo    [USAGE] Si les ports sont occupes par d'autres applications
echo.
echo === DEMARRAGE DE L'APPLICATION ===
echo.
echo 5. start_promptachat_manual.bat
echo    [DESC] Demarrage complet de l'application (RECOMMANDE)
echo    [USAGE] Lance backend + frontend avec verifications
echo.
echo 6. start_backend_manual.bat
echo    [DESC] Demarrage du backend uniquement
echo    [USAGE] Pour les developpeurs ou tests backend
echo.
echo 7. start_frontend_manual.bat
echo    [DESC] Demarrage du frontend uniquement  
echo    [USAGE] Pour les developpeurs ou tests frontend
echo.
echo === PROCEDURE RECOMMANDEE ===
echo.
echo Pour une premiere installation :
echo   1. cd windows
echo   2. check_installation.bat     (diagnostic)
echo   3. resoudre_problemes.bat     (correction auto)
echo   4. liberer_ports.bat          (si ports occupes)
echo   5. start_promptachat_manual.bat (demarrage)
echo.
echo Pour un demarrage normal :
echo   - cd windows
echo   - start_promptachat_manual.bat
echo.
echo === INFORMATIONS UTILES ===
echo.
echo URLs d'acces une fois demarre :
echo   - Frontend : http://localhost:3000
echo   - Backend  : http://localhost:8001  
echo   - API Docs : http://localhost:8001/docs
echo.
echo Connexion par defaut :
echo   - Utilisateur : admin
echo   - Mot de passe : admin
echo.
echo === ENVIRONNEMENT CONDA ===
echo.
echo L'application utilise l'environnement conda 'promptachat'
echo Commandes utiles :
echo   - conda activate promptachat   (activer)
echo   - conda deactivate             (desactiver)
echo   - conda env list               (lister environnements)
echo.
echo === ARCHITECTURE DU PROJET ===
echo.
echo Structure des fichiers :
echo   promptachat/                (racine du projet)
echo   ├── windows/                (scripts Windows - VOUS ETES ICI)
echo   ├── backend/                (serveur Python FastAPI)
echo   ├── frontend/               (interface React)
echo   ├── config.ini              (configuration)
echo   └── README.md               (documentation principale)
echo.
echo === SUPPORT ===
echo.
echo En cas de probleme :
echo   1. Executez check_installation.bat pour diagnostiquer
echo   2. Suivez les recommandations affichees
echo   3. Consultez la documentation : ../README.md
echo   4. Documentation Windows : INSTALLATION_WINDOWS.md
echo.
pause 