# PromptAchat - Bibliothèque de Prompts pour la Filière Achat

![PromptAchat](https://img.shields.io/badge/PromptAchat-v1.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.x-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.x-009688.svg)
![SQLite](https://img.shields.io/badge/SQLite-Local-003B57.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)

PromptAchat est une application web complète dédiée à la gestion et l'utilisation de prompts IA pour les équipes Achat. Elle permet de créer, organiser et exécuter des prompts avec des LLMs locaux (Ollama) ou des plateformes externes (ChatGPT, Claude, etc.).

## 🚀 Fonctionnalités Principales

- **🔐 Authentification hybride** : LDAP + base locale SQLite
- **📚 Bibliothèque de prompts** : Système et utilisateur, internes et externes
- **⚡ Exécution temps réel** : Streaming avec serveurs LLM multiples
- **🤖 Gestion serveurs LLM** : Configuration et test de multiples serveurs
- **📄 Support PDF** : Extraction automatique de texte pour contexte (stockage local)
- **🔍 Vérification confidentialité** : Analyse automatique des données sensibles
- **👥 Gestion utilisateurs** : Panel d'administration complet
- **📝 Éditeur avancé** : Variables dynamiques et aperçu temps réel
- **⚙️ Préférences utilisateur** : Sélection de serveurs et modèles préférés

## 🏃‍♂️ Installation Rapide

### 🪟 Option 1: Installation Windows Simplifiée (RECOMMANDÉE)

**Installation sans droits administrateur, sans Docker, sans MongoDB !**

```powershell
# Windows PowerShell (en tant qu'utilisateur normal)
git clone <votre-repo>
cd promptachat
cd windows
.\install_windows_simple.ps1
```

**Cette installation :**
- ✅ Installe automatiquement Miniconda (si nécessaire)
- ✅ Utilise uniquement SQLite + stockage fichiers local
- ✅ Pas de MongoDB, pas de Docker
- ✅ Fonctionne sans droits administrateur
- ✅ Crée des scripts de démarrage automatiques

**Après installation :**
```bat
# Depuis le répertoire windows/
cd windows

# Démarrage complet de l'application
.\start_promptachat_manual.bat

# Ou démarrage séparé
.\start_backend_manual.bat    # Backend seul
.\start_frontend_manual.bat   # Frontend seul

# Outils de diagnostic et maintenance
.\check_installation.bat      # Diagnostic complet
.\resoudre_problemes.bat     # Résolution automatique des problèmes
.\aide.bat                   # Aide et documentation
```

### 🐳 Option 2: Installation Docker (Développeurs)

```bash
# Linux/macOS
git clone <votre-repo>
cd promptachat
chmod +x install.sh
./install.sh

# Windows (PowerShell en administrateur)
git clone <votre-repo>
cd promptachat
.\install.ps1
```

### 🔧 Option 3: Docker Compose

```bash
git clone <votre-repo>
cd promptachat
make install  # ou docker-compose up -d
```

### 📦 Option 4: Makefile (Développeurs)

```bash
make help      # Voir toutes les commandes
make install   # Installation complète
make start     # Démarrer l'application
make logs      # Voir les logs
make stop      # Arrêter
```

## 📋 Commandes Principales

| Commande | Description |
|----------|-------------|
| `make start` | Démarrer l'application |
| `make stop` | Arrêter l'application |
| `make logs` | Voir les logs en temps réel |
| `make health` | Vérifier l'état des services |
| `make backup` | Sauvegarder la base de données |
| `make update` | Mettre à jour l'application |

## 🔧 Configuration

### Serveurs LLM

Configurez vos serveurs LLM dans `config.ini` :

```ini
[llm_servers]
# Serveur Ollama local
ollama = ollama|http://localhost:11434|none|llama3

# API OpenAI
openai = openai|https://api.openai.com/v1|sk-your-key|gpt-3.5-turbo

# Serveur interne
internal = openai|http://your-server:8080/v1|your-token|llama3
```

### LDAP Entreprise

```ini
[ldap]
enabled = true
server = ldap.yourcompany.com
user_dn_format = uid=%%s,ou=employees,dc=company,dc=com
```

### Stockage des Fichiers

```ini
[file_storage]
storage_type = filesystem
base_directory = uploaded_files
max_file_size_mb = 10
allowed_extensions = pdf
```

## 📊 Architecture

### Version Simplifiée (Windows/Local)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   SQLite +      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   Local Files   │
│   Port 3000     │    │   Port 8001     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │              ┌─────────────────┐              
         └──────────────►│   LLM Servers   │
                         │   (Ollama, etc.)│
                         │   Port 11434    │
                         └─────────────────┘
```

### Version Docker (Développement)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   MongoDB       │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   Port 3000     │    │   Port 8001     │    │   Port 27017    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   LLM Servers   │◄─────────────┘
                         │   (Ollama, etc.)│
                         │   Port 11434    │
                         └─────────────────┘
```

## 🌐 URLs d'Accès

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Documentation API**: http://localhost:8001/docs

## 👤 Connexion par Défaut

- **Utilisateur**: `admin`
- **Mot de passe**: `admin`

⚠️ **Important**: Changez ce mot de passe en production !

## 🪟 Spécifique Windows - Installation Sans Administrateur

### Prérequis Minimaux
- **Windows 10/11**
- **PowerShell 5.0+** (inclus par défaut)
- **Droits utilisateur normaux** (pas d'admin requis)
- **Connexion Internet** pour télécharger Miniconda

### Processus d'Installation Automatisé

```powershell
# 1. Cloner le dépôt
git clone <votre-repo>
cd promptachat

# 2. Aller dans le répertoire Windows
cd windows

# 3. Lancer l'installation automatique
.\install_windows_simple.ps1

# 4. Suivre les instructions à l'écran
# 5. Une fois terminé, lancer l'application
.\start_promptachat_manual.bat
```

### 📚 Documentation Windows Complète

Pour une documentation détaillée de l'installation Windows, consultez :
**[windows/INSTALLATION_WINDOWS.md](windows/INSTALLATION_WINDOWS.md)**

### 🛠️ Scripts Windows Disponibles

Tous les scripts Windows sont maintenant organisés dans le répertoire `windows/` :

| Script | Description |
|--------|-------------|
| `install_windows_simple.ps1` | **Installation automatique complète** |
| `start_promptachat_manual.bat` | **Démarrage complet** (recommandé) |
| `start_backend_manual.bat` | Démarrage backend seul |
| `start_frontend_manual.bat` | Démarrage frontend seul |
| `check_installation.bat` | Diagnostic complet de l'installation |
| `resoudre_problemes.bat` | Résolution automatique des problèmes |
| `fix_npm_issue.bat` | Correction spécifique npm/Node.js |
| `liberer_ports.bat` | Libération des ports 3000/8001 |
| `aide.bat` | Aide et guide d'utilisation |

### 🎯 Démarrage Rapide Windows

```powershell
# Depuis la racine du projet
cd windows

# Pour une première installation
.\check_installation.bat      # Diagnostic
.\resoudre_problemes.bat     # Correction automatique
.\start_promptachat_manual.bat # Démarrage

# Pour un démarrage normal
.\start_promptachat_manual.bat

# En cas de problème
.\aide.bat                   # Aide complète
```

### 🛠️ Installation Manuelle Windows avec Conda

Si vous préférez installer manuellement ou personnaliser l'installation :

#### Étape 1 : Installation de Miniconda

```powershell
# Télécharger Miniconda depuis https://docs.conda.io/en/latest/miniconda.html
# Ou via PowerShell (optionnel) :
Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -OutFile "$env:TEMP\miniconda-installer.exe"

# Lancer l'installation
Start-Process -FilePath "$env:TEMP\miniconda-installer.exe" -Wait

# IMPORTANT : Cocher "Add to PATH" pendant l'installation
# Ou ajouter manuellement après installation
```

#### Étape 2 : Redémarrer PowerShell et Vérifier Conda

```powershell
# Fermer et rouvrir PowerShell
# Vérifier que conda fonctionne
conda --version

# Si conda n'est pas reconnu, ajouter au PATH manuellement :
# $env:PATH += ";C:\Users\$env:USERNAME\miniconda3\Scripts;C:\Users\$env:USERNAME\miniconda3"
```

#### Étape 3 : Créer l'Environnement Conda

```powershell
# Créer un nouvel environnement avec Python 3.11 et Node.js
conda create -n promptachat python=3.11 nodejs=18 -y

# Activer l'environnement
conda activate promptachat

# Vérifier l'activation (le prompt doit montrer (promptachat))
```

#### Étape 4 : Cloner et Configurer le Projet

```powershell
# Cloner le projet (si pas déjà fait)
git clone <votre-repo>
cd promptachat

# Copier la configuration
copy config.ini.template config.ini

# Créer les répertoires nécessaires
mkdir backend\uploaded_files
mkdir backend\data
mkdir logs
```

#### Étape 5 : Installation des Dépendances Backend

```powershell
# Aller dans le dossier backend
cd backend

# Vérifier que l'environnement conda est activé
conda activate promptachat

# Installer les dépendances Python essentielles
pip install fastapi uvicorn python-dotenv pydantic sqlalchemy

# Installer les dépendances pour l'authentification
pip install pyjwt bcrypt

# Installer les dépendances pour les fichiers
pip install python-multipart PyPDF2

# Installer les dépendances optionnelles pour les services LLM
pip install requests aiohttp

# Retourner au dossier racine
cd ..
```

#### Étape 6 : Installation des Dépendances Frontend

```powershell
# Aller dans le dossier frontend
cd frontend

# S'assurer que npm est disponible
npm --version

# Installer les dépendances Node.js
npm install

# Retourner au dossier racine
cd ..
```

#### Étape 7 : Configuration de l'Application

```powershell
# Éditer le fichier config.ini selon vos besoins
notepad config.ini

# Configuration minimale pour démarrer :
# [llm_servers]
# # Décommenter et configurer selon vos serveurs LLM disponibles
# 
# [file_storage]
# storage_type = filesystem
# base_directory = uploaded_files
# max_file_size_mb = 10
```

#### Étape 8 : Test de l'Installation

```powershell
# Tester le backend
conda activate promptachat
cd backend
python -c "import fastapi, uvicorn, sqlalchemy; print('✅ Backend dependencies OK')"

# Tester le frontend
cd ../frontend  
npm list --depth=0 | findstr react
cd ..
```

#### Étape 9 : Utiliser les Scripts Automatiques

```powershell
# Aller dans le répertoire des scripts Windows
cd windows

# Utiliser les scripts automatiques (recommandé)
.\start_promptachat_manual.bat
```

#### Étape 10 : Premier Démarrage

```powershell
# Depuis windows/
.\start_promptachat_manual.bat

# Ou lancer séparément :
# Backend seul : .\start_backend_manual.bat
# Frontend seul : .\start_frontend_manual.bat
```

#### Étape 11 : Vérification du Fonctionnement

1. **Backend** : Ouvrir http://localhost:8001/docs
2. **Frontend** : Ouvrir http://localhost:3000
3. **Connexion** : admin / admin

#### 🔧 Dépannage Installation Manuelle

**Problème : Conda non reconnu**
```powershell
# Ajouter Conda au PATH manuellement
$condaPath = "$env:USERPROFILE\miniconda3"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$condaPath;$condaPath\Scripts", "User")
# Redémarrer PowerShell
```

**Problème : Erreur lors de pip install**
```powershell
# Mettre à jour pip
conda activate promptachat
python -m pip install --upgrade pip

# Installer avec cache désactivé
pip install --no-cache-dir fastapi uvicorn python-dotenv
```

**Problème : Erreur npm install**
```powershell
# Nettoyer le cache npm
npm cache clean --force

# Supprimer node_modules et réinstaller
cd frontend
rmdir /s node_modules
npm install
```

**Problème : Port occupé**
```powershell
# Utiliser le script automatique
cd windows
.\liberer_ports.bat

# Ou manuellement
netstat -ano | findstr :3000
netstat -ano | findstr :8001
taskkill /F /PID <numero_processus>
```

#### 📦 Personnalisation de l'Installation

**Changer le nom de l'environnement Conda :**
```powershell
conda create -n mon-promptachat python=3.11 nodejs=18
conda activate mon-promptachat
# Puis modifier les scripts .bat pour utiliser "mon-promptachat"
```

**Installer des dépendances supplémentaires :**
```powershell
conda activate promptachat
# Pour Ollama local
pip install ollama
# Pour d'autres services LLM
pip install openai anthropic
```

**Configuration avancée :**
```ini
# Dans config.ini
[file_storage]
base_directory = D:\mes_fichiers_promptachat  # Chemin personnalisé
max_file_size_mb = 50                         # Taille de fichier plus importante

[llm_servers]
ollama_local = ollama|http://localhost:11434|none|llama3
openai_api = openai|https://api.openai.com/v1|YOUR_API_KEY|gpt-4
```

### Architecture de Stockage Locale

**Base de données utilisateurs** : `user_auth.db` (SQLite)
**Prompts système** : `prompts.json` (JSON)
**Prompts utilisateur** : `user_prompts.json` (JSON)
**Fichiers uploadés** : `backend/uploaded_files/` (Système de fichiers)

### Avantages de cette Architecture

- ✅ **Pas de MongoDB** - Installation simplifiée
- ✅ **Pas de Docker** - Fonctionne directement sur Windows
- ✅ **Pas de droits admin** - Installation utilisateur via Conda
- ✅ **Démarrage rapide** - Scripts batch automatiques
- ✅ **Maintenance facile** - Fichiers locaux visibles
- ✅ **Scripts organisés** - Tous dans le répertoire `windows/`