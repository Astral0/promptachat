# 🚀 Guide d'Installation PromptAchat

## 📋 Options d'Installation

1. **🐳 Docker Compose (RECOMMANDÉ)** - Installation automatisée complète
2. **💻 Installation Manuelle** - Contrôle total, toutes plateformes
3. **🔧 Script d'Installation** - Semi-automatisé

---

## 🐳 Option 1: Installation Docker (RECOMMANDÉ)

### Prérequis
- **Docker Desktop** (Windows/macOS) ou **Docker Engine** (Linux)
- **Docker Compose** (inclus avec Docker Desktop)

### Installation Docker Desktop

**Windows :**
```bash
# Télécharger Docker Desktop depuis https://docker.com/products/docker-desktop/
# Activer WSL2 (recommandé pour de meilleures performances)
```

**macOS :**
```bash
# Télécharger Docker Desktop depuis https://docker.com/products/docker-desktop/
# Ou via Homebrew:
brew install --cask docker
```

**Linux (Ubuntu/Debian) :**
```bash
# Installation Docker Engine
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
```

### Déploiement avec Docker Compose

**1. Cloner le projet**
```bash
git clone <votre-repo-promptachat>
cd promptachat
```

**2. Créer docker-compose.yml**
```yaml
version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:7.0
    container_name: promptachat-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: promptachat
      MONGO_INITDB_ROOT_PASSWORD: promptachat_password_2024
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - promptachat-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: promptachat-backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://promptachat:promptachat_password_2024@mongodb:27017/promptachat_db?authSource=admin
      - DB_NAME=promptachat_db
    volumes:
      - ./config.ini:/app/config.ini
      - ./prompts.json:/app/prompts.json
      - ./user_prompts.json:/app/user_prompts.json
      - user_auth_data:/app
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    networks:
      - promptachat-network

  # Frontend React
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: promptachat-frontend
    restart: unless-stopped
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - promptachat-network

  # Ollama (Optionnel - pour LLM local)
  ollama:
    image: ollama/ollama:latest
    container_name: promptachat-ollama
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - promptachat-network
    # Décommentez pour GPU support (NVIDIA)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

volumes:
  mongodb_data:
  ollama_data:
  user_auth_data:

networks:
  promptachat-network:
    driver: bridge
```

**3. Créer les Dockerfiles**

**Backend Dockerfile :**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile :**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Install serve for production
RUN yarn global add serve

# Expose port
EXPOSE 3000

# Serve the built application
CMD ["serve", "-s", "build", "-l", "3000"]
```

**4. Configuration**
```bash
# Copier la configuration template
cp config.ini.template config.ini

# Modifier config.ini selon vos besoins
nano config.ini
```

**5. Démarrage**
```bash
# Construire et démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Accéder à l'application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# MongoDB: localhost:27017
```

**6. Configuration Ollama (Optionnel)**
```bash
# Télécharger un modèle dans Ollama
docker exec -it promptachat-ollama ollama pull llama3

# Ou depuis l'host
curl http://localhost:11434/api/pull -d '{"name":"llama3"}'
```

**7. Gestion**
```bash
# Arrêter l'application
docker-compose down

# Redémarrer
docker-compose restart

# Mise à jour
git pull
docker-compose build
docker-compose up -d

# Voir l'utilisation des ressources
docker stats
```

---

## 💻 Option 2: Installation Manuelle

### Prérequis Généraux
- **Node.js** 18+ et **Yarn**
- **Python** 3.9+ et **pip**
- **MongoDB** 5.0+
- **Git**

### Installation sur Windows

**1. Prérequis Windows**
```powershell
# Installer Chocolatey (gestionnaire de paquets Windows)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installer les dépendances
choco install nodejs python mongodb git -y
choco install yarn -y

# Ou télécharger manuellement :
# Node.js: https://nodejs.org/
# Python: https://python.org/downloads/
# MongoDB: https://www.mongodb.com/try/download/community
# Git: https://git-scm.com/download/win
```

**2. Configuration MongoDB Windows**
```powershell
# Démarrer MongoDB comme service
net start MongoDB

# Ou manuellement
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
```

**3. Configuration Python Windows**
```powershell
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r backend\requirements.txt
```

**4. Lancement Windows**
```powershell
# Terminal 1 - Backend
cd backend
..\venv\Scripts\activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn install
yarn start

# Terminal 3 - Ollama (optionnel)
# Télécharger depuis https://ollama.ai
ollama serve
ollama pull llama3
```

### Installation sur macOS

**1. Prérequis macOS**
```bash
# Installer Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer les dépendances
brew install node python mongodb/brew/mongodb-community yarn git
```

**2. Configuration MongoDB macOS**
```bash
# Démarrer MongoDB
brew services start mongodb/brew/mongodb-community

# Ou manuellement
mongod --config /usr/local/etc/mongod.conf
```

**3. Lancement macOS**
```bash
# Même procédure que Linux ci-dessous
```

### Installation sur Linux (Ubuntu/Debian)

**1. Prérequis Linux**
```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installer Node.js et Yarn
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g yarn

# Installer Python
sudo apt install -y python3 python3-pip python3-venv

# Installer MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Démarrer MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**2. Installation Application**
```bash
# Cloner le projet
git clone <votre-repo>
cd promptachat

# Configuration backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration frontend
cd ../frontend
yarn install

# Configuration application
cd ..
cp config.ini.template config.ini
# Modifier config.ini selon vos besoins
```

**3. Lancement Linux**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn start

# Terminal 3 - Ollama (optionnel)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3
```

---

## 🔧 Option 3: Script d'Installation Automatisé

**Script d'installation pour Linux/macOS :**
```bash
#!/bin/bash
# install.sh

set -e

echo "🚀 Installation PromptAchat"

# Détection OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ OS non supporté par ce script. Utilisez l'installation manuelle."
    exit 1
fi

# Installation des dépendances
if [ "$OS" = "linux" ]; then
    sudo apt update
    sudo apt install -y nodejs npm python3 python3-pip python3-venv mongodb git
    sudo npm install -g yarn
elif [ "$OS" = "macos" ]; then
    if ! command -v brew &> /dev/null; then
        echo "Installation de Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install node python mongodb/brew/mongodb-community yarn git
fi

# Cloner le projet (si pas déjà fait)
if [ ! -d "promptachat" ]; then
    git clone <votre-repo> promptachat
fi
cd promptachat

# Configuration backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Configuration frontend
cd frontend
yarn install
cd ..

# Configuration
cp config.ini.template config.ini

# Démarrage MongoDB
if [ "$OS" = "linux" ]; then
    sudo systemctl start mongod
    sudo systemctl enable mongod
elif [ "$OS" = "macos" ]; then
    brew services start mongodb/brew/mongodb-community
fi

echo "✅ Installation terminée !"
echo "🌐 Démarrez l'application avec : ./start.sh"
```

**Script de démarrage :**
```bash
#!/bin/bash
# start.sh

# Fonction de nettoyage
cleanup() {
    echo "🛑 Arrêt de l'application..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "🚀 Démarrage PromptAchat..."

# Démarrage backend
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# Attendre que le backend démarre
sleep 5

# Démarrage frontend
cd frontend
yarn start &
FRONTEND_PID=$!
cd ..

echo "✅ Application démarrée !"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8001"
echo "📊 MongoDB: localhost:27017"
echo ""
echo "👤 Connexion par défaut:"
echo "   Utilisateur: admin"
echo "   Mot de passe: admin"
echo ""
echo "Press Ctrl+C to stop"

# Attendre
wait
```

---

## 🎯 Configuration Post-Installation

### 1. Configuration des Serveurs LLM

**Modifier `config.ini` :**
```ini
[llm_servers]
# Serveur Ollama local
ollama_local = ollama|http://localhost:11434|none|llama3

# API OpenAI (si vous avez une clé)
openai = openai|https://api.openai.com/v1|sk-your-api-key|gpt-3.5-turbo

# Serveur LLM interne de votre entreprise
internal = openai|http://votre-serveur-llm:8080/v1|votre-token|llama3
```

### 2. Configuration LDAP (Entreprise)

```ini
[ldap]
enabled = true
server = ldap.votre-entreprise.com
port = 389
user_dn_format = uid=%%s,ou=employees,dc=entreprise,dc=com
base_dn = dc=entreprise,dc=com
```

### 3. Sécurisation

```ini
[security]
jwt_secret_key = $(openssl rand -base64 32)
initial_admin_uids = votre_uid_admin
```

---

## 🔧 Maintenance et Mise à Jour

### Docker
```bash
# Mise à jour
git pull
docker-compose build
docker-compose up -d

# Sauvegarde des données
docker-compose exec mongodb mongodump --out /data/backup

# Restauration
docker-compose exec mongodb mongorestore /data/backup
```

### Manuel
```bash
# Mise à jour du code
git pull

# Mise à jour des dépendances backend
cd backend && source venv/bin/activate && pip install -r requirements.txt

# Mise à jour des dépendances frontend
cd frontend && yarn install

# Redémarrage
./start.sh
```

---

## 🆘 Dépannage

### Problèmes Courants

**Port déjà utilisé :**
```bash
# Trouver le processus
lsof -i :3000  # ou :8001, :27017
kill -9 <PID>
```

**MongoDB ne démarre pas :**
```bash
# Linux
sudo systemctl status mongod
sudo journalctl -u mongod

# Docker
docker-compose logs mongodb
```

**Permissions Python (Windows) :**
```powershell
# Exécuter PowerShell en tant qu'administrateur
Set-ExecutionPolicy RemoteSigned
```

---

## 📋 Résumé des Recommandations

| Scenario | Recommandation |
|----------|----------------|
| **Production entreprise** | 🐳 Docker Compose |
| **Développement local** | 💻 Installation manuelle |
| **Démo rapide** | 🐳 Docker Compose |
| **Windows utilisateur** | 🐳 Docker Desktop |
| **Serveur Linux** | 🐳 Docker Compose |

**Docker Compose est recommandé** car il :
- ✅ Automatise tout (MongoDB, etc.)
- ✅ Fonctionne sur toutes les plateformes
- ✅ Isole l'environnement
- ✅ Facilite les mises à jour
- ✅ Simplifie le déploiement

Quelle option préférez-vous pour votre installation ?