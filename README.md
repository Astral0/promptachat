# PromptAchat - Bibliothèque de Prompts pour la Filière Achat

![PromptAchat](https://img.shields.io/badge/PromptAchat-v1.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.x-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.x-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.x-47A248.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)

PromptAchat est une application web complète dédiée à la gestion et l'utilisation de prompts IA pour les équipes Achat. Elle permet de créer, organiser et exécuter des prompts avec des LLMs locaux (Ollama) ou des plateformes externes (ChatGPT, Claude, etc.).

## 🚀 Fonctionnalités Principales

- **🔐 Authentification hybride** : LDAP + base locale SQLite
- **📚 Bibliothèque de prompts** : Système et utilisateur, internes et externes
- **⚡ Exécution temps réel** : Streaming avec serveurs LLM multiples
- **🤖 Gestion serveurs LLM** : Configuration et test de multiples serveurs
- **📄 Support PDF** : Extraction automatique de texte pour contexte
- **🔍 Vérification confidentialité** : Analyse automatique des données sensibles
- **👥 Gestion utilisateurs** : Panel d'administration complet
- **📝 Éditeur avancé** : Variables dynamiques et aperçu temps réel
- **⚙️ Préférences utilisateur** : Sélection de serveurs et modèles préférés

## 🏃‍♂️ Installation Rapide

### Option 1: Installation Automatisée (Recommandée)

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

### Option 2: Docker Compose

```bash
git clone <votre-repo>
cd promptachat
make install  # ou docker-compose up -d
```

### Option 3: Makefile (Développeurs)

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

## 📊 Architecture

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
- **MongoDB**: localhost:27017

## 👤 Connexion par Défaut

- **Utilisateur**: `admin`
- **Mot de passe**: `admin`

⚠️ **Important**: Changez ce mot de passe en production !

## 🐳 Installation avec Docker

### Prérequis
- Docker Desktop (Windows/macOS) ou Docker Engine (Linux)
- Docker Compose
- 4GB RAM minimum
- 10GB espace disque

### Démarrage Rapide
```bash
# Cloner et démarrer
git clone <votre-repo>
cd promptachat
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### Services Inclus
- ✅ **Frontend React** (Port 3000)
- ✅ **Backend FastAPI** (Port 8001)  
- ✅ **MongoDB** (Port 27017)
- ✅ **Ollama** (Port 11434) - Optionnel
- ✅ **Nginx** (Port 80/443) - Production

## 💻 Installation Manuelle

### Prérequis
- **Node.js** 18+ et **Yarn**
- **Python** 3.9+ et **pip**
- **MongoDB** 5.0+
- **Git**

### Installation des Dépendances

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nodejs npm python3 python3-pip mongodb git
npm install -g yarn
```

**macOS:**
```bash
brew install node python mongodb git yarn
```

**Windows:**
```powershell
choco install nodejs python mongodb git yarn
```

### Configuration

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
yarn install

# Configuration
cd ..
cp config.ini.template config.ini
```

### Démarrage

```bash
# Terminal 1 - MongoDB
mongod

# Terminal 2 - Backend
cd backend && source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 - Frontend
cd frontend && yarn start
```

## 🤖 Configuration Ollama

### Installation Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Télécharger depuis https://ollama.ai
```

### Téléchargement Modèles

```bash
# Démarrer Ollama
ollama serve

# Télécharger des modèles
ollama pull llama3
ollama pull codellama
ollama pull mistral
```

### Configuration dans PromptAchat

```ini
[llm_servers]
ollama_local = ollama|http://localhost:11434|none|llama3
```

## 🔐 Sécurité et Production

### Configuration Sécurisée

```ini
[security]
jwt_secret_key = $(openssl rand -base64 32)
initial_admin_uids = your_admin_uid

[ldap]
enabled = true
server = ldap.company.com
use_ssl = true
```

### Déploiement Production

```bash
# Avec Nginx reverse proxy
make start-prod

# Ou
docker-compose --profile production up -d
```

### HTTPS avec SSL

1. Placez vos certificats dans `nginx/ssl/`
2. Modifiez `nginx/nginx.conf`
3. Redémarrez Nginx

## 📊 Monitoring et Maintenance

### Surveillance

```bash
# Statut des services
make status

# Santé des services
make health

# Utilisation des ressources
make monitor

# Logs en temps réel
make logs
```

### Sauvegarde

```bash
# Sauvegarde automatique
make backup

# Restauration
make restore BACKUP_FILE=backups/promptachat_backup_20241201_120000.gz
```

### Mise à Jour

```bash
# Mise à jour complète
make update

# Ou manuellement
git pull
docker-compose build
docker-compose up -d
```

## 🛠️ Développement

### Configuration Développement

```bash
# Setup environnement local
make dev-setup

# Démarrage mode dev avec hot reload
make start-dev

# Tests
make test
```

### Structure du Projet

```
promptachat/
├── backend/           # API FastAPI
│   ├── server.py     # Serveur principal
│   ├── models.py     # Modèles Pydantic
│   ├── services/     # Services métier
│   └── Dockerfile    # Image Docker
├── frontend/         # Interface React
│   ├── src/
│   │   ├── App.js   # App principale
│   │   └── components/ # Composants React
│   └── Dockerfile   # Image Docker
├── nginx/           # Configuration Nginx
├── scripts/         # Scripts d'initialisation
├── docker-compose.yml # Configuration Docker
├── Makefile         # Commandes automatisées
└── install.sh       # Script d'installation
```

## 🆘 Dépannage

### Problèmes Courants

**Port déjà utilisé:**
```bash
# Trouver le processus
lsof -i :3000  # ou :8001, :27017
kill -9 <PID>
```

**Docker ne démarre pas:**
```bash
# Vérifier Docker
docker --version
docker-compose --version

# Redémarrer Docker
sudo systemctl restart docker  # Linux
# Redémarrer Docker Desktop    # Windows/macOS
```

**MongoDB inaccessible:**
```bash
# Vérifier le service
docker-compose logs mongodb

# Redémarrer MongoDB
docker-compose restart mongodb
```

**Erreurs de permissions:**
```bash
# Linux - Ajouter utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

### Support et Logs

```bash
# Logs détaillés
docker-compose logs -f --tail=100

# Accès aux conteneurs
docker-compose exec backend bash
docker-compose exec mongodb mongosh

# Nettoyage
make clean
```

## 📚 Documentation

- **📖 Guide d'installation**: [INSTALLATION.md](INSTALLATION.md)
- **🔧 Configuration**: [config.ini.template](config.ini.template)
- **🤖 API Documentation**: http://localhost:8001/docs
- **📊 Architecture**: Voir diagrammes ci-dessus

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 🆘 Support

- **Issues**: Utilisez le système d'issues GitHub
- **Email**: contact@votre-entreprise.fr
- **Documentation**: Ce README et [INSTALLATION.md](INSTALLATION.md)

---

**Développé avec ❤️ pour optimiser les processus d'achat avec l'IA**

🚀 **Prêt à révolutionner vos achats avec l'IA ? Lancez `make install` !**