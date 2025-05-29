# PromptAchat - Bibliothèque de Prompts pour la Filière Achat

![PromptAchat](https://img.shields.io/badge/PromptAchat-v1.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.x-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.x-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.x-47A248.svg)

PromptAchat est une application web complète dédiée à la gestion et l'utilisation de prompts IA pour les équipes Achat. Elle permet de créer, organiser et exécuter des prompts avec des LLMs locaux (Ollama) ou des plateformes externes (ChatGPT, Claude, etc.).

## 🚀 Fonctionnalités Principales

- **🔐 Authentification hybride** : LDAP + base locale SQLite
- **📚 Bibliothèque de prompts** : Système et utilisateur, internes et externes
- **⚡ Exécution temps réel** : Streaming avec Ollama et génération pour plateformes externes
- **📄 Support PDF** : Extraction automatique de texte pour contexte
- **🔍 Vérification confidentialité** : Analyse automatique des données sensibles
- **👥 Gestion utilisateurs** : Panel d'administration complet
- **📝 Éditeur avancé** : Variables dynamiques et aperçu temps réel

## 📋 Prérequis

### Obligatoires
- **Node.js** >= 18.x
- **Python** >= 3.9
- **MongoDB** >= 5.x
- **Yarn** (pour le frontend)

### Optionnels
- **Ollama** (pour l'exécution de prompts internes)
- **Serveur LDAP** (pour l'authentification d'entreprise)

## 🛠️ Installation et Configuration

### 1. Clonage du Projet

```bash
git clone <votre-repo>
cd promptachat
```

### 2. Configuration de MongoDB

**Option A : MongoDB Local**
```bash
# Installation sur Ubuntu/Debian
sudo apt update
sudo apt install -y mongodb

# Démarrage du service
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Vérification
mongo --eval "db.adminCommand('ismaster')"
```

**Option B : MongoDB avec Docker**
```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

### 3. Configuration du Backend

```bash
cd backend

# Installation des dépendances Python
python -m pip install -r requirements.txt

# Configuration de l'environnement
cp .env.example .env
```

**Modifiez le fichier `.env` :**
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=promptachat_db
```

### 4. Configuration de l'Application

```bash
# Copiez le fichier de configuration template
cp config.ini.template config.ini
```

**Modifiez `config.ini` selon vos besoins :**

```ini
[app]
name = edf  # ou enedis
title = PromptAchat - Bibliothèque de Prompts EDF
logo_url = https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/EDF_logo.svg/1200px-EDF_logo.svg.png
contact_email = contact@votre-entreprise.fr

[ollama]
enabled = true
url = http://localhost:11434/v1
default_model = llama3

[ldap]
enabled = false  # Mettez true si vous avez un serveur LDAP
server = ldap.votre-entreprise.com
port = 389
user_dn_format = uid=%%s,ou=people,dc=votre-entreprise,dc=com

[security]
initial_admin_uids = admin,votre_uid  # UIDs des admins initiaux
jwt_secret_key = CHANGEZ_MOI_EN_PRODUCTION_AVEC_VALEUR_ALEATOIRE
```

### 5. Configuration du Frontend

```bash
cd frontend

# Installation des dépendances
yarn install

# Configuration de l'environnement
cp .env.example .env
```

**Modifiez le fichier `.env` :**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 6. Installation d'Ollama (Optionnel)

**Sur Linux/macOS :**
```bash
curl -fsSL https://ollama.ai/install.sh | sh

# Téléchargement d'un modèle
ollama pull llama3
```

**Sur Windows :** Téléchargez depuis [ollama.ai](https://ollama.ai)

## 🚀 Lancement de l'Application

### Option A : Lancement Manuel

**Terminal 1 - MongoDB (si pas déjà lancé) :**
```bash
mongod
```

**Terminal 2 - Backend :**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 3 - Frontend :**
```bash
cd frontend
yarn start
```

**Terminal 4 - Ollama (optionnel) :**
```bash
ollama serve
```

### Option B : Avec Docker Compose (Avancé)

```bash
# Créez un docker-compose.yml
docker-compose up -d
```

## 🔐 Premier Démarrage

### 1. Accès à l'Application

Ouvrez votre navigateur sur : [http://localhost:3000](http://localhost:3000)

### 2. Connexion Administrateur

**Identifiants par défaut :**
- **Utilisateur :** `admin`
- **Mot de passe :** `admin`

⚠️ **Important :** Changez ce mot de passe en production !

### 3. Vérification du Fonctionnement

1. **Tableau de bord** : Vérifiez que les statistiques s'affichent
2. **Bibliothèque** : Explorez les prompts système pré-configurés
3. **Nouveau prompt** : Créez un prompt de test
4. **Exécution** : Testez avec un prompt externe d'abord

## 📚 Utilisation

### Création d'un Prompt

1. **Aller dans "Bibliothèque"**
2. **Cliquer "Nouveau prompt"**
3. **Remplir les informations :**
   - Titre descriptif
   - Type (Interne pour Ollama, Externe pour ChatGPT/Claude)
   - Contenu avec variables `{nom_variable}`
   - Catégorie pour l'organisation

### Variables Dynamiques

Utilisez des variables dans vos prompts :
```
Analysez ce contrat pour {nom_entreprise}.
Budget disponible : {budget}
Critères : {criteres_specifiques}
```

### Exécution de Prompts

**Prompts Internes :**
- Exécutés avec Ollama en streaming
- Réponses en temps réel dans l'interface

**Prompts Externes :**
- Génération de texte optimisé
- Vérification automatique de confidentialité
- Liens vers plateformes externes

## 🔧 Configuration Avancée

### LDAP (Entreprise)

```ini
[ldap]
enabled = true
server = ldap.entreprise.com
port = 389
user_dn_format = uid=%%s,ou=employees,dc=entreprise,dc=com
use_ssl = false
base_dn = dc=entreprise,dc=com
```

### LLM Interne

```ini
[internal]
url = http://votre-llm-interne:8080/v1
api_key = votre_cle_api
default_model = votre_modele
```

### OneAPI Gateway

```ini
[oneapi]
use_oneapi = true
oneapi_url = http://localhost:3000/v1
api_key = votre_cle_oneapi
```

## 🐛 Dépannage

### Backend ne démarre pas

```bash
# Vérifiez les logs
tail -f /var/log/promptachat/backend.log

# Vérifiez MongoDB
mongo --eval "db.adminCommand('ismaster')"

# Vérifiez les dépendances
pip install -r requirements.txt
```

### Frontend ne se compile pas

```bash
# Nettoyage du cache
rm -rf node_modules package-lock.json
yarn install

# Vérifiez les variables d'environnement
cat .env
```

### Ollama non accessible

```bash
# Vérifiez le service
ollama list

# Test manuel
curl http://localhost:11434/api/version

# Redémarrage
ollama serve
```

### Problèmes d'authentification

```bash
# Vérifiez la base de données utilisateurs
sqlite3 user_auth.db "SELECT * FROM users;"

# Réinitialisation admin
rm user_auth.db
# Redémarrer le backend
```

## 📁 Structure du Projet

```
promptachat/
├── backend/                 # API FastAPI
│   ├── server.py           # Serveur principal
│   ├── models.py           # Modèles Pydantic
│   ├── config.py           # Gestionnaire de configuration
│   └── services/           # Services métier
│       ├── auth_service.py # Authentification
│       ├── prompt_service.py # Gestion prompts
│       └── llm_service.py  # Intégration LLM
├── frontend/               # Interface React
│   ├── src/
│   │   ├── App.js         # Application principale
│   │   └── components/    # Composants React
├── config.ini             # Configuration principale
├── prompts.json           # Prompts système
├── user_prompts.json      # Prompts utilisateur
└── user_auth.db          # Base utilisateurs locale
```

## 🔒 Sécurité

### En Développement
- Utilisateurs admin par défaut
- JWT avec secret par défaut
- Pas de vérification HTTPS

### En Production
- Changez `jwt_secret_key` dans `config.ini`
- Configurez HTTPS
- Utilisez des vraies bases de données
- Activez l'authentification LDAP
- Surveillez les logs

## 📊 Monitoring

### Logs

```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend  
tail -f /var/log/supervisor/frontend.out.log

# MongoDB
tail -f /var/log/mongodb/mongod.log
```

### Health Check

- **Backend :** [http://localhost:8001/api/health](http://localhost:8001/api/health)
- **Frontend :** [http://localhost:3000](http://localhost:3000)

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation :** Ce README
- **Issues :** Utilisez le système d'issues GitHub
- **Email :** contact@votre-entreprise.fr

---

**Développé avec ❤️ pour optimiser les processus d'achat avec l'IA**