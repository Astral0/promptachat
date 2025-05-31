# 🪟 Installation Windows Simplifiée - PromptAchat

**Installation sans droits administrateur, sans Docker, sans MongoDB !**

## ✅ Prérequis

- **Windows 10 ou 11**
- **PowerShell 5.0+** (inclus par défaut)
- **Connexion Internet** pour télécharger les dépendances
- **Pas de droits administrateur requis !**

## 🚀 Installation Automatique (Recommandée)

### Étape 1 : Cloner le Projet

```powershell
# Ouvrir PowerShell en tant qu'utilisateur normal
git clone <votre-repo>
cd promptachat
```

### Étape 2 : Accéder au Répertoire Windows

```powershell
# Aller dans le répertoire des scripts Windows
cd windows
```

### Étape 3 : Lancer l'Installation Automatique

```powershell
# Lancer le diagnostic complet
.\check_installation.bat

# Puis résoudre automatiquement les problèmes
.\resoudre_problemes.bat
```

### Étape 4 : Démarrer l'Application

```bat
# Démarrage complet de l'application
.\start_promptachat_manual.bat
```

## 🎯 Démarrage Rapide

Depuis le répertoire `windows/`, vous avez accès à ces scripts :

| Script | Description |
|--------|-------------|
| `start_promptachat_manual.bat` | **Démarrage complet** (recommandé) |
| `start_backend_manual.bat` | Backend seul (développement) |
| `start_frontend_manual.bat` | Frontend seul (développement) |

## 🏗️ Architecture Sans MongoDB

```
📁 promptachat/
├── 📄 config.ini               ← Configuration principale
├── 📁 windows/                 ← Scripts Windows (VOUS ÊTES ICI)
│   ├── 📄 *.bat               ← Tous les scripts d'installation/démarrage
│   └── 📄 INSTALLATION_WINDOWS.md ← Ce guide
├── 📁 backend/
│   ├── 📁 uploaded_files/      ← Fichiers PDF uploadés
│   ├── 📄 server.py            ← API FastAPI (modifiée)
│   ├── 📄 user_auth.db         ← Base utilisateurs (SQLite)
│   └── 📁 data/                ← Données temporaires
├── 📁 frontend/                ← Interface React
├── 📄 prompts.json             ← Prompts système (JSON)
└── 📄 user_prompts.json        ← Prompts utilisateur (JSON)
```

## 🔧 Avantages de cette Architecture

- ✅ **Installation simple** : Pas de MongoDB complexe
- ✅ **Pas de Docker** : Fonctionne directement sur Windows
- ✅ **Pas de droits admin** : Installation utilisateur via Conda
- ✅ **Données visibles** : Fichiers SQLite/JSON accessibles
- ✅ **Sauvegarde facile** : Copier/coller les fichiers
- ✅ **Scripts organisés** : Tous dans le répertoire `windows/`

## 📊 URLs d'Accès

Une fois démarré, accédez à :

- 🌐 **Frontend** : http://localhost:3000
- ⚡ **Backend API** : http://localhost:8001  
- 📚 **Documentation API** : http://localhost:8001/docs

## 👤 Première Connexion

**Utilisateur** : `admin`  
**Mot de passe** : `admin`

⚠️ **Changez ce mot de passe après la première connexion !**

## 🛠️ Installation Manuelle Détaillée

Si vous préférez installer manuellement, depuis le répertoire `windows/` :

### Étape 1 : Diagnostic

```powershell
# Identifier les problèmes
.\check_installation.bat
```

### Étape 2 : Résolution Ciblée

```powershell
# Si npm manque
.\fix_npm_issue.bat

# Si ports occupés
.\liberer_ports.bat

# Ou résolution automatique complète
.\resoudre_problemes.bat
```

### Étape 3 : Configuration Manuelle

```powershell
# Copier la configuration si nécessaire
copy ..\config.ini.template ..\config.ini

# Créer les répertoires manquants
mkdir ..\backend\uploaded_files
```

### Étape 4 : Installation Dépendances

```powershell
# Activer l'environnement conda
conda activate promptachat

# Installer dépendances Python manquantes
pip install sqlalchemy

# Installer dépendances frontend si nécessaire
cd ..\frontend
npm install
cd ..\windows
```

## ⚙️ Configuration Avancée

### Modifier la Configuration

Éditez le fichier `..\config.ini` :

```ini
[file_storage]
storage_type = filesystem
base_directory = uploaded_files
max_file_size_mb = 10
allowed_extensions = pdf

[llm_servers]
# Ajouter vos serveurs LLM
ollama = ollama|http://localhost:11434|none|llama3
openai = openai|https://api.openai.com/v1|YOUR_API_KEY|gpt-3.5-turbo
```

### Ajouter Ollama Local (Optionnel)

```powershell
# Télécharger Ollama depuis https://ollama.ai
# Puis installer un modèle
ollama pull llama3
```

## 💾 Sauvegarde et Restauration

### Sauvegarde Simple

```powershell
# Aller à la racine du projet
cd ..

# Créer un dossier de sauvegarde
mkdir backup_$(Get-Date -Format "yyyyMMdd_HHmmss")

# Copier les fichiers importants
copy user_auth.db backup_*/
copy user_prompts.json backup_*/
copy -r backend/uploaded_files backup_*/
```

### Restauration

```powershell
# Restaurer depuis une sauvegarde
copy backup_20241201_120000/user_auth.db .
copy backup_20241201_120000/user_prompts.json .
copy -r backup_20241201_120000/uploaded_files backend/
```

## 🆘 Dépannage

### Erreur "Execution Policy"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Script ne trouve pas les fichiers

```powershell
# Vérifiez que vous êtes dans le bon répertoire
pwd
# Vous devriez être dans promptachat/windows/

# Si vous êtes ailleurs, naviguez vers le bon répertoire
cd chemin/vers/promptachat/windows
```

### Port 3000 ou 8001 Occupé

```powershell
# Utiliser le script de libération
.\liberer_ports.bat

# Ou manuellement
netstat -ano | findstr :3000
taskkill /F /PID <numéro_du_processus>
```

### Conda Non Reconnu

```powershell
# Redémarrer PowerShell après installation Miniconda
# Puis relancer les scripts depuis windows/
.\fix_npm_issue.bat
```

### Réinstallation Complète

```powershell
# Supprimer l'environnement Conda
conda env remove -n promptachat

# Recréer l'environnement
conda create -n promptachat python=3.11 nodejs=18 -y

# Relancer la résolution
.\resoudre_problemes.bat
```

## 🔄 Mise à Jour

```powershell
# Retourner à la racine pour git
cd ..

# Mettre à jour le code source
git pull

# Retourner dans windows/
cd windows

# Réinstaller les dépendances si nécessaire
.\resoudre_problemes.bat
```

## 📈 Monitoring

### Surveiller l'Utilisation

- **Taille des fichiers** : Vérifier `..\backend\uploaded_files\`
- **Base utilisateurs** : Taille de `..\user_auth.db`
- **Logs** : Consulter les consoles de démarrage

### Nettoyage

```powershell
# Nettoyer les fichiers temporaires
cd ..
del backend\uploaded_files\*_metadata.json
del backend\__pycache__ -r
del frontend\node_modules\.cache -r
cd windows
```

## 🎯 Performance

### Optimisations Windows

1. **Antivirus** : Exclure le dossier `promptachat/` du scan en temps réel
2. **Windows Defender** : Ajouter une exception pour Python/Node.js
3. **Disque** : Utiliser un SSD si possible pour de meilleures performances

### Mémoire Recommandée

- **Minimum** : 4 GB RAM
- **Recommandé** : 8 GB RAM
- **Optimal** : 16 GB RAM (pour gros modèles Ollama)

## 🔐 Sécurité

### Configuration Sécurisée

Éditez `..\config.ini` :

```ini
[security]
jwt_secret_key = GenerezUneCleSecurisee123!
initial_admin_uids = votre_admin_uid

[ldap]
enabled = true  # Si vous avez un serveur LDAP
server = ldap.votre-entreprise.com
```

### Recommandations

- 🔑 Changez le mot de passe admin
- 🔐 Configurez LDAP si disponible  
- 🛡️ Utilisez HTTPS en production
- 📂 Limitez l'accès au dossier `backend\uploaded_files\`

## 🌟 Fonctionnalités

### Gestion des Fichiers PDF

- ✅ Upload de fichiers PDF jusqu'à 10 MB
- ✅ Extraction automatique du texte
- ✅ Stockage sécurisé par utilisateur
- ✅ Téléchargement des fichiers originaux

### Gestion des Prompts

- ✅ Prompts système (lecture seule)
- ✅ Prompts utilisateur (créer, modifier, supprimer)
- ✅ Partage de prompts publics
- ✅ Duplication de prompts
- ✅ Variables dynamiques

### Intégration LLM

- ✅ Support Ollama local
- ✅ Support OpenAI API
- ✅ Serveurs LLM multiples
- ✅ Streaming des réponses
- ✅ Vérification de confidentialité

## 📋 Procédure Complète Recommandée

```powershell
# 1. Cloner le projet
git clone <votre-repo>
cd promptachat

# 2. Aller dans le répertoire Windows
cd windows

# 3. Aide si nécessaire
.\aide.bat

# 4. Diagnostic complet
.\check_installation.bat

# 5. Résolution automatique
.\resoudre_problemes.bat

# 6. Libération des ports si nécessaire
.\liberer_ports.bat

# 7. Démarrage de l'application
.\start_promptachat_manual.bat
```

## 🎉 C'est Parti !

Votre installation PromptAchat Windows est maintenant prête !

**Prochaines étapes :**
1. 🚀 Lancez `start_promptachat_manual.bat`
2. 🌐 Ouvrez http://localhost:3000
3. 👤 Connectez-vous avec admin/admin
4. 🔧 Configurez vos serveurs LLM
5. 📝 Créez vos premiers prompts !

**Support :**
- 📖 Documentation complète : [../README.md](../README.md)
- 🔧 Configuration : [../config.ini.template](../config.ini.template)
- 🛠️ Scripts d'aide : `aide.bat`
- 🐛 Issues : GitHub Issues
- 📧 Support : contact@votre-entreprise.fr 