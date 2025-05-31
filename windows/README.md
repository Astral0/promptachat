# 🪟 Scripts Windows - PromptAchat

Ce répertoire contient tous les scripts et outils spécifiques à Windows pour PromptAchat.

## 📁 Organisation

Tous les scripts Windows ont été organisés dans ce répertoire pour éviter l'encombrement de la racine du projet.

## 🚀 Démarrage Rapide

```powershell
# Depuis la racine du projet
cd windows

# Première installation
.\check_installation.bat      # Diagnostic
.\resoudre_problemes.bat     # Résolution automatique
.\start_promptachat_manual.bat # Démarrage

# Démarrage normal
.\start_promptachat_manual.bat
```

## 📋 Scripts Disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `install_windows_simple.ps1` | **Installation automatique complète** | Première installation |
| `start_promptachat_manual.bat` | **Démarrage complet** (recommandé) | Utilisation normale |
| `start_backend_manual.bat` | Démarrage backend seul | Développement |
| `start_frontend_manual.bat` | Démarrage frontend seul | Développement |
| `check_installation.bat` | Diagnostic complet | Dépannage |
| `resoudre_problemes.bat` | Résolution automatique | Dépannage |
| `fix_npm_issue.bat` | Correction npm/Node.js | Problème spécifique |
| `liberer_ports.bat` | Libération ports 3000/8001 | Problème spécifique |
| `aide.bat` | Aide et guide complet | Information |

## 📚 Documentation Complète

- **Guide d'installation détaillé** : [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)
- **Documentation générale** : [../README.md](../README.md)

## 🎯 Procédure Recommandée

### Première Installation

```powershell
cd windows
.\install_windows_simple.ps1  # Installation automatique PowerShell
# OU
.\check_installation.bat      # Diagnostic manuel
.\resoudre_problemes.bat     # Résolution manuelle
```

### Démarrage Quotidien

```powershell
cd windows
.\start_promptachat_manual.bat
```

### En cas de Problème

```powershell
cd windows
.\aide.bat                   # Guide complet
.\check_installation.bat     # Diagnostic
.\resoudre_problemes.bat     # Résolution automatique
```

## ⚡ URLs d'Accès

Une fois démarré :
- **Frontend** : http://localhost:3000
- **Backend** : http://localhost:8001
- **API Docs** : http://localhost:8001/docs

## 👤 Connexion

- **Utilisateur** : `admin`
- **Mot de passe** : `admin`

## 🛠️ Architecture

Ces scripts utilisent l'architecture simplifiée sans MongoDB :
- **Base utilisateurs** : SQLite (../user_auth.db)
- **Prompts** : JSON (../prompts.json, ../user_prompts.json)
- **Fichiers** : Système local (../backend/uploaded_files/)

## 🔧 Prérequis

- Windows 10/11
- PowerShell 5.0+
- Pas de droits administrateur requis
- Connexion Internet (pour téléchargement Miniconda)

## 📞 Support

- **Scripts d'aide** : `aide.bat`
- **Documentation** : [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)
- **Issues** : GitHub Issues du projet principal 