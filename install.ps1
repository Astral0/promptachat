# install.ps1 - Script d'installation PowerShell pour Windows

param(
    [switch]$Docker,
    [switch]$Manual,
    [switch]$Help
)

# Couleurs pour l'affichage
$colors = @{
    'Red' = 'Red'
    'Green' = 'Green'
    'Yellow' = 'Yellow'
    'Blue' = 'Cyan'
    'White' = 'White'
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════╗
║                    PromptAchat Installer                     ║
║              Bibliothèque de Prompts IA - EDF               ║
║                      Version Windows                        ║
╚══════════════════════════════════════════════════════════════╝
"@ -Color 'Blue'
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Chocolatey {
    Write-ColorOutput "🍫 Installation de Chocolatey..." -Color 'Blue'
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-ColorOutput "✅ Chocolatey déjà installé" -Color 'Green'
        return
    }
    
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    Write-ColorOutput "✅ Chocolatey installé" -Color 'Green'
}

function Install-DockerDesktop {
    Write-ColorOutput "🐳 Installation de Docker Desktop..." -Color 'Blue'
    
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-ColorOutput "✅ Docker déjà installé" -Color 'Green'
        docker --version
        return
    }
    
    choco install docker-desktop -y
    
    Write-ColorOutput "✅ Docker Desktop installé" -Color 'Green'
    Write-ColorOutput "⚠️  Redémarrage requis pour finaliser l'installation Docker" -Color 'Yellow'
}

function Install-ManualDependencies {
    Write-ColorOutput "📦 Installation des dépendances manuelles..." -Color 'Blue'
    
    # Install Node.js, Python, MongoDB, Git
    $packages = @('nodejs', 'python', 'mongodb', 'git', 'yarn')
    
    foreach ($package in $packages) {
        Write-ColorOutput "📥 Installation de $package..." -Color 'Blue'
        choco install $package -y
    }
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-ColorOutput "✅ Dépendances installées" -Color 'Green'
}

function Setup-Application {
    Write-ColorOutput "🔧 Configuration de l'application..." -Color 'Blue'
    
    # Create config from template
    if (-not (Test-Path "config.ini")) {
        Copy-Item "config.ini.template" "config.ini"
        Write-ColorOutput "✅ Fichier de configuration créé" -Color 'Green'
    }
    
    if ($Manual) {
        # Backend setup
        Write-ColorOutput "🔧 Configuration du backend..." -Color 'Blue'
        Set-Location "backend"
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        pip install --upgrade pip
        pip install -r requirements.txt
        Set-Location ".."
        
        # Frontend setup
        Write-ColorOutput "🔧 Configuration du frontend..." -Color 'Blue'
        Set-Location "frontend"
        yarn install
        Set-Location ".."
        
        Write-ColorOutput "✅ Application configurée" -Color 'Green'
    }
}

function Generate-Scripts {
    Write-ColorOutput "📝 Génération des scripts de démarrage..." -Color 'Blue'
    
    if ($Docker) {
        # Docker scripts
        @'
@echo off
echo 🚀 Démarrage PromptAchat avec Docker...
docker-compose up -d
echo ✅ Application démarrée!
echo 🌐 Frontend: http://localhost:3000
echo 🔌 Backend: http://localhost:8001
echo 📊 MongoDB: localhost:27017
echo.
echo 👤 Connexion par défaut:
echo    Utilisateur: admin
echo    Mot de passe: admin
pause
'@ | Out-File -FilePath "start.bat" -Encoding utf8

        @'
@echo off
echo 🛑 Arrêt PromptAchat...
docker-compose down
echo ✅ Application arrêtée
pause
'@ | Out-File -FilePath "stop.bat" -Encoding utf8

    } else {
        # Manual scripts
        @'
@echo off
echo 🚀 Démarrage PromptAchat...

echo ⚡ Démarrage du backend...
cd backend
call venv\Scripts\activate.bat
start /B uvicorn server:app --host 0.0.0.0 --port 8001 --reload
cd ..

timeout /t 5 > nul

echo ⚡ Démarrage du frontend...
cd frontend
start /B yarn start
cd ..

echo ✅ Application démarrée!
echo 🌐 Frontend: http://localhost:3000
echo 🔌 Backend: http://localhost:8001
echo.
echo 👤 Connexion par défaut:
echo    Utilisateur: admin
echo    Mot de passe: admin
echo.
echo Appuyez sur une touche pour arrêter...
pause > nul

echo 🛑 Arrêt de l'application...
taskkill /F /IM "uvicorn.exe" 2>nul
taskkill /F /IM "node.exe" 2>nul
'@ | Out-File -FilePath "start.bat" -Encoding utf8
    }
    
    Write-ColorOutput "✅ Scripts générés" -Color 'Green'
}

function Install-Ollama {
    $installOllama = Read-Host "Installer Ollama pour LLM local ? (y/N)"
    
    if ($installOllama -match '^[Yy]$') {
        Write-ColorOutput "🤖 Installation d'Ollama..." -Color 'Blue'
        
        if ($Docker) {
            Write-ColorOutput "ℹ️  Ollama sera installé via Docker" -Color 'Blue'
        } else {
            # Download and install Ollama for Windows
            $ollamaUrl = "https://ollama.ai/download/windows"
            Write-ColorOutput "📥 Téléchargement d'Ollama depuis $ollamaUrl" -Color 'Blue'
            Write-ColorOutput "⚠️  Installation manuelle requise depuis le navigateur" -Color 'Yellow'
            Start-Process $ollamaUrl
        }
    }
}

function Show-Help {
    Write-ColorOutput @"
PromptAchat Windows Installer

UTILISATION:
    .\install.ps1 [-Docker] [-Manual] [-Help]

OPTIONS:
    -Docker     Installation avec Docker Desktop (Recommandé)
    -Manual     Installation manuelle des dépendances
    -Help       Affiche cette aide

EXEMPLES:
    .\install.ps1 -Docker    # Installation Docker
    .\install.ps1 -Manual    # Installation manuelle
    .\install.ps1            # Mode interactif

PRÉREQUIS:
    - Windows 10/11
    - PowerShell 5.0+
    - Connexion Internet
    - Droits administrateur

APRÈS INSTALLATION:
    - Exécutez start.bat pour démarrer l'application
    - Accédez à http://localhost:3000
    - Connectez-vous avec admin/admin
"@ -Color 'White'
}

function Main {
    Write-Banner
    
    if ($Help) {
        Show-Help
        return
    }
    
    # Check administrator rights
    if (-not (Test-Administrator)) {
        Write-ColorOutput "❌ Ce script doit être exécuté en tant qu'administrateur" -Color 'Red'
        Write-ColorOutput "➡️  Clic droit sur PowerShell > Exécuter en tant qu'administrateur" -Color 'Yellow'
        exit 1
    }
    
    # Installation mode selection
    if (-not $Docker -and -not $Manual) {
        Write-ColorOutput "Choisissez le mode d'installation:" -Color 'Blue'
        Write-ColorOutput "1) Docker (Recommandé - Installation complète automatisée)" -Color 'White'
        Write-ColorOutput "2) Manuel (Installation native sur Windows)" -Color 'White'
        
        $choice = Read-Host "Votre choix (1-2)"
        
        switch ($choice) {
            '1' { $Docker = $true }
            '2' { $Manual = $true }
            default {
                Write-ColorOutput "❌ Choix invalide" -Color 'Red'
                exit 1
            }
        }
    }
    
    Write-ColorOutput "ℹ️  Début de l'installation PromptAchat" -Color 'Blue'
    
    # Install Chocolatey
    Install-Chocolatey
    
    # Install dependencies based on mode
    if ($Docker) {
        Write-ColorOutput "ℹ️  Installation Docker sélectionnée" -Color 'Blue'
        Install-DockerDesktop
    } else {
        Write-ColorOutput "ℹ️  Installation manuelle sélectionnée" -Color 'Blue'
        Install-ManualDependencies
        
        # Start MongoDB service
        Write-ColorOutput "🔧 Démarrage du service MongoDB..." -Color 'Blue'
        Start-Service MongoDB -ErrorAction SilentlyContinue
    }
    
    # Setup application
    Setup-Application
    
    # Generate scripts
    Generate-Scripts
    
    # Optional Ollama
    Install-Ollama
    
    # Final instructions
    Write-ColorOutput ""
    Write-ColorOutput "🎉 Installation terminée avec succès!" -Color 'Green'
    Write-ColorOutput ""
    Write-ColorOutput "Pour démarrer l'application:" -Color 'Blue'
    Write-ColorOutput "  Double-cliquez sur start.bat" -Color 'White'
    Write-ColorOutput ""
    Write-ColorOutput "URLs d'accès:" -Color 'Blue'
    Write-ColorOutput "  🌐 Application: http://localhost:3000" -Color 'White'
    Write-ColorOutput "  🔌 API Backend: http://localhost:8001" -Color 'White'
    Write-ColorOutput "  📊 MongoDB: localhost:27017" -Color 'White'
    Write-ColorOutput ""
    Write-ColorOutput "Identifiants par défaut:" -Color 'Blue'
    Write-ColorOutput "  👤 Utilisateur: admin" -Color 'White'
    Write-ColorOutput "  🔑 Mot de passe: admin" -Color 'White'
    Write-ColorOutput ""
    Write-ColorOutput "⚠️  Changez le mot de passe admin en production!" -Color 'Yellow'
    Write-ColorOutput ""
    Write-ColorOutput "🚀 Bonne utilisation de PromptAchat!" -Color 'Green'
    
    if ($Docker) {
        Write-ColorOutput ""
        Write-ColorOutput "⚠️  Si Docker Desktop a été installé, un redémarrage peut être nécessaire" -Color 'Yellow'
    }
}

# Execute main function
Main