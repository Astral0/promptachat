# Installation Windows Simplifiée - PromptAchat
# Installation automatique sans droits administrateur, sans Docker, sans MongoDB

Write-Host "[INSTALLATION] PromptAchat - Installation Windows Simplifiee" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Vérification des prérequis
Write-Host "[VERIFICATION] Verification des prerequis..." -ForegroundColor Yellow

# Vérification de PowerShell
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "[ERREUR] PowerShell 5.0+ requis. Version actuelle: $($PSVersionTable.PSVersion)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] PowerShell version: $($PSVersionTable.PSVersion)" -ForegroundColor Green

# Vérification de l'emplacement du script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "[INFO] Script execute depuis: $scriptDir" -ForegroundColor Cyan
Write-Host "[INFO] Racine du projet: $projectRoot" -ForegroundColor Cyan

# Vérification de la structure du projet
$requiredPaths = @(
    "$projectRoot\backend",
    "$projectRoot\frontend", 
    "$projectRoot\config.ini.template"
)

foreach ($path in $requiredPaths) {
    if (Test-Path $path) {
        Write-Host "[OK] Trouve: $path" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Manquant: $path" -ForegroundColor Red
        Write-Host "[INFO] Assurez-vous d'etre dans le repertoire 'windows' du projet PromptAchat" -ForegroundColor Yellow
        exit 1
    }
}

# Installation de Miniconda
Write-Host ""
Write-Host "[ETAPE 1] Installation de Miniconda (si necessaire)..." -ForegroundColor Yellow

$condaPath = "$env:USERPROFILE\miniconda3\Scripts\conda.exe"
if (Test-Path $condaPath) {
    Write-Host "[OK] Miniconda deja installe" -ForegroundColor Green
} else {
    Write-Host "[INFO] Telechargement de Miniconda..." -ForegroundColor Cyan
    $minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $installerPath = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"
    
    try {
        Invoke-WebRequest -Uri $minicondaUrl -OutFile $installerPath
        Write-Host "[OK] Miniconda telecharge" -ForegroundColor Green
        
        Write-Host "[INFO] Installation de Miniconda (sans droits admin)..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "/InstallationType=JustMe", "/RegisterPython=0", "/S", "/D=$env:USERPROFILE\miniconda3" -Wait
        
        # Ajouter Conda au PATH pour cette session
        $env:PATH = "$env:USERPROFILE\miniconda3\Scripts;$env:USERPROFILE\miniconda3;$env:PATH"
        
        Write-Host "[OK] Miniconda installe avec succes" -ForegroundColor Green
        Write-Host "[INFO] Redemarrez PowerShell apres l'installation pour utiliser les scripts .bat" -ForegroundColor Yellow
    }
    catch {
        Write-Host "[ERREUR] Echec de l'installation de Miniconda: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Configuration de Conda
Write-Host ""
Write-Host "[ETAPE 2] Configuration de l'environnement Conda..." -ForegroundColor Yellow

try {
    # Initialiser conda pour PowerShell
    & "$env:USERPROFILE\miniconda3\Scripts\conda.exe" init powershell
    
    # Créer l'environnement promptachat
    Write-Host "[INFO] Creation de l'environnement 'promptachat'..." -ForegroundColor Cyan
    & "$env:USERPROFILE\miniconda3\Scripts\conda.exe" create -n promptachat python=3.11 nodejs=18 -y -c conda-forge
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Environnement conda 'promptachat' cree avec succes" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Echec de la creation de l'environnement conda" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "[ERREUR] Erreur lors de la configuration conda: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Installation des dépendances Python
Write-Host ""
Write-Host "[ETAPE 3] Installation des dependances Python..." -ForegroundColor Yellow

try {
    # Activer l'environnement et installer les dépendances
    & "$env:USERPROFILE\miniconda3\Scripts\conda.exe" activate promptachat
    & "$env:USERPROFILE\miniconda3\envs\promptachat\Scripts\pip.exe" install -r "$projectRoot\backend\requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependances Python installees" -ForegroundColor Green
    } else {
        Write-Host "[ATTENTION] Erreur lors de l'installation des dependances Python" -ForegroundColor Yellow
        Write-Host "[INFO] Vous pourrez les installer manuellement plus tard" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "[ATTENTION] Erreur Python: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Installation des dépendances frontend
Write-Host ""
Write-Host "[ETAPE 4] Installation des dependances frontend..." -ForegroundColor Yellow

try {
    Set-Location "$projectRoot\frontend"
    & "$env:USERPROFILE\miniconda3\envs\promptachat\Scripts\npm.exe" install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependances frontend installees" -ForegroundColor Green
    } else {
        Write-Host "[ATTENTION] Erreur lors de l'installation des dependances frontend" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ATTENTION] Erreur frontend: $($_.Exception.Message)" -ForegroundColor Yellow
}
finally {
    Set-Location $scriptDir
}

# Configuration des fichiers
Write-Host ""
Write-Host "[ETAPE 5] Configuration des fichiers..." -ForegroundColor Yellow

# Copier config.ini si nécessaire
if (-not (Test-Path "$projectRoot\config.ini")) {
    if (Test-Path "$projectRoot\config.ini.template") {
        Copy-Item "$projectRoot\config.ini.template" "$projectRoot\config.ini"
        Write-Host "[OK] Fichier config.ini cree depuis le template" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Template config.ini.template manquant" -ForegroundColor Red
    }
} else {
    Write-Host "[OK] Fichier config.ini existe deja" -ForegroundColor Green
}

# Créer le répertoire uploaded_files
$uploadDir = "$projectRoot\backend\uploaded_files"
if (-not (Test-Path $uploadDir)) {
    New-Item -ItemType Directory -Path $uploadDir -Force
    Write-Host "[OK] Repertoire uploaded_files cree" -ForegroundColor Green
} else {
    Write-Host "[OK] Repertoire uploaded_files existe deja" -ForegroundColor Green
}

# Création des scripts de démarrage
Write-Host ""
Write-Host "[ETAPE 6] Les scripts de demarrage sont deja disponibles dans le repertoire windows/" -ForegroundColor Yellow
Write-Host "[INFO] Scripts disponibles:" -ForegroundColor Cyan
Write-Host "  - start_promptachat_manual.bat (demarrage complet)" -ForegroundColor Cyan
Write-Host "  - start_backend_manual.bat (backend seul)" -ForegroundColor Cyan  
Write-Host "  - start_frontend_manual.bat (frontend seul)" -ForegroundColor Cyan
Write-Host "  - check_installation.bat (diagnostic)" -ForegroundColor Cyan
Write-Host "  - resoudre_problemes.bat (resolution automatique)" -ForegroundColor Cyan

# Test final
Write-Host ""
Write-Host "[ETAPE 7] Test final de l'installation..." -ForegroundColor Yellow

$testPassed = $true

# Test conda
try {
    & "$env:USERPROFILE\miniconda3\Scripts\conda.exe" info --envs | Out-String
    Write-Host "[OK] Conda fonctionne" -ForegroundColor Green
}
catch {
    Write-Host "[ATTENTION] Probleme avec conda" -ForegroundColor Yellow
    $testPassed = $false
}

# Test environnement
$envPath = "$env:USERPROFILE\miniconda3\envs\promptachat"
if (Test-Path $envPath) {
    Write-Host "[OK] Environnement 'promptachat' cree" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Environnement 'promptachat' non trouve" -ForegroundColor Yellow
    $testPassed = $false
}

# Résumé final
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALLATION TERMINEE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($testPassed) {
    Write-Host "[SUCCES] PromptAchat est installe et pret a l'utilisation !" -ForegroundColor Green
    Write-Host ""
    Write-Host "[PROCHAINES ETAPES]" -ForegroundColor Yellow
    Write-Host "1. Redemarrez PowerShell pour que conda soit disponible" -ForegroundColor Cyan
    Write-Host "2. cd windows" -ForegroundColor Cyan
    Write-Host "3. .\start_promptachat_manual.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[ACCES]" -ForegroundColor Yellow
    Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  - Backend:  http://localhost:8001" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[CONNEXION INITIALE]" -ForegroundColor Yellow
    Write-Host "  Utilisateur: admin" -ForegroundColor Cyan
    Write-Host "  Mot de passe: admin" -ForegroundColor Cyan
} else {
    Write-Host "[ATTENTION] Installation partiellement reussie" -ForegroundColor Yellow
    Write-Host "[ACTION] Executez le diagnostic:" -ForegroundColor Yellow
    Write-Host "  cd windows" -ForegroundColor Cyan
    Write-Host "  .\check_installation.bat" -ForegroundColor Cyan
    Write-Host "  .\resoudre_problemes.bat" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "[AIDE] Pour de l'aide, executez: .\aide.bat" -ForegroundColor Yellow
Write-Host ""

# Pause finale
Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 