#!/bin/bash
# install.sh - Script d'installation automatisé pour PromptAchat

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    PromptAchat Installer                     ║
║              Bibliothèque de Prompts IA - EDF               ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "Ce script ne doit pas être exécuté en tant que root"
   exit 1
fi

# OS Detection
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    DISTRO="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    DISTRO="Windows"
else
    log_error "OS non supporté: $OSTYPE"
    log_info "Utilisez l'installation manuelle ou Docker"
    exit 1
fi

log_info "OS détecté: $DISTRO ($OS)"

# Installation mode selection
echo ""
log_info "Choisissez le mode d'installation:"
echo "1) Docker (Recommandé - Installation complète automatisée)"
echo "2) Manuel (Installation native sur le système)"
echo "3) Développement (Installation pour développeurs)"
echo ""
read -p "Votre choix (1-3): " INSTALL_MODE

case $INSTALL_MODE in
    1)
        log_info "Installation Docker sélectionnée"
        INSTALL_TYPE="docker"
        ;;
    2)
        log_info "Installation manuelle sélectionnée"
        INSTALL_TYPE="manual"
        ;;
    3)
        log_info "Installation développement sélectionnée"
        INSTALL_TYPE="dev"
        ;;
    *)
        log_error "Choix invalide"
        exit 1
        ;;
esac

# Docker Installation
install_docker() {
    log_info "Installation de Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker déjà installé"
        docker --version
    else
        if [[ $OS == "linux" ]]; then
            # Install Docker on Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            
        elif [[ $OS == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install --cask docker
            else
                log_error "Homebrew non installé. Installez Docker Desktop manuellement depuis https://docker.com"
                exit 1
            fi
        fi
        
        log_success "Docker installé avec succès"
        log_warning "Vous devez redémarrer votre session pour utiliser Docker sans sudo"
        log_info "Ou exécutez: newgrp docker"
    fi
    
    # Verify Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose non trouvé"
        exit 1
    fi
    
    log_success "Docker Compose version: $(docker-compose --version)"
}

# Manual Installation
install_manual() {
    log_info "Installation manuelle des dépendances..."
    
    # Install Node.js and Yarn
    if ! command -v node &> /dev/null; then
        log_info "Installation de Node.js..."
        if [[ $OS == "linux" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [[ $OS == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install node
            else
                log_error "Homebrew requis pour l'installation sur macOS"
                exit 1
            fi
        fi
    fi
    
    if ! command -v yarn &> /dev/null; then
        log_info "Installation de Yarn..."
        sudo npm install -g yarn
    fi
    
    # Install Python
    if ! command -v python3 &> /dev/null; then
        log_info "Installation de Python..."
        if [[ $OS == "linux" ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
        elif [[ $OS == "macos" ]]; then
            brew install python
        fi
    fi
    
    # Install MongoDB
    if ! command -v mongod &> /dev/null; then
        log_info "Installation de MongoDB..."
        if [[ $OS == "linux" ]]; then
            wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
            echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
            sudo apt update
            sudo apt install -y mongodb-org
            sudo systemctl enable mongod
            sudo systemctl start mongod
        elif [[ $OS == "macos" ]]; then
            brew tap mongodb/brew
            brew install mongodb-community
            brew services start mongodb/brew/mongodb-community
        fi
    fi
    
    log_success "Dépendances installées"
}

# Setup application
setup_application() {
    log_info "Configuration de l'application..."
    
    # Create config from template
    if [[ ! -f "config.ini" ]]; then
        cp config.ini.template config.ini
        log_success "Fichier de configuration créé"
    fi
    
    if [[ $INSTALL_TYPE == "manual" ]] || [[ $INSTALL_TYPE == "dev" ]]; then
        # Backend setup
        log_info "Configuration du backend..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        cd ..
        
        # Frontend setup
        log_info "Configuration du frontend..."
        cd frontend
        yarn install
        cd ..
        
        log_success "Application configurée"
    fi
}

# Generate start scripts
generate_scripts() {
    log_info "Génération des scripts de démarrage..."
    
    if [[ $INSTALL_TYPE == "docker" ]]; then
        # Docker scripts
        cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Démarrage PromptAchat avec Docker..."
docker-compose up -d
echo "✅ Application démarrée!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8001"
echo "📊 MongoDB: localhost:27017"
echo ""
echo "👤 Connexion par défaut:"
echo "   Utilisateur: admin"
echo "   Mot de passe: admin"
EOF

        cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt PromptAchat..."
docker-compose down
echo "✅ Application arrêtée"
EOF

        cat > update.sh << 'EOF'
#!/bin/bash
echo "🔄 Mise à jour PromptAchat..."
git pull
docker-compose build
docker-compose up -d
echo "✅ Mise à jour terminée"
EOF

    else
        # Manual scripts
        cat > start.sh << 'EOF'
#!/bin/bash

# Fonction de nettoyage
cleanup() {
    echo "🛑 Arrêt de l'application..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "🚀 Démarrage PromptAchat..."

# Vérifier MongoDB
if ! pgrep mongod > /dev/null; then
    echo "⚠️  MongoDB n'est pas démarré. Tentative de démarrage..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mongod
    elif command -v brew &> /dev/null; then
        brew services start mongodb/brew/mongodb-community
    else
        mongod --fork --logpath /var/log/mongodb.log
    fi
fi

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
EOF
    fi
    
    chmod +x start.sh stop.sh update.sh 2>/dev/null || true
    log_success "Scripts générés"
}

# Install Ollama (optional)
install_ollama() {
    echo ""
    read -p "Installer Ollama pour LLM local ? (y/N): " INSTALL_OLLAMA
    
    if [[ $INSTALL_OLLAMA =~ ^[Yy]$ ]]; then
        log_info "Installation d'Ollama..."
        
        if [[ $INSTALL_TYPE == "docker" ]]; then
            log_info "Ollama sera installé via Docker"
        else
            if [[ $OS == "linux" ]] || [[ $OS == "macos" ]]; then
                curl -fsSL https://ollama.ai/install.sh | sh
                
                # Start Ollama
                if [[ $OS == "linux" ]]; then
                    sudo systemctl enable ollama
                    sudo systemctl start ollama
                fi
                
                # Download a model
                log_info "Téléchargement du modèle llama3..."
                ollama pull llama3
                
                log_success "Ollama installé avec le modèle llama3"
            else
                log_warning "Installation manuelle d'Ollama requise sur Windows"
                log_info "Téléchargez depuis: https://ollama.ai"
            fi
        fi
    fi
}

# Main installation flow
main() {
    log_info "Début de l'installation PromptAchat"
    
    # Install dependencies based on mode
    if [[ $INSTALL_TYPE == "docker" ]]; then
        install_docker
    else
        install_manual
    fi
    
    # Setup application
    setup_application
    
    # Generate scripts
    generate_scripts
    
    # Optional Ollama
    install_ollama
    
    # Final instructions
    echo ""
    log_success "Installation terminée avec succès! 🎉"
    echo ""
    log_info "Pour démarrer l'application:"
    echo "  ./start.sh"
    echo ""
    
    if [[ $INSTALL_TYPE == "docker" ]]; then
        log_info "Commandes Docker utiles:"
        echo "  docker-compose logs -f    # Voir les logs"
        echo "  docker-compose restart    # Redémarrer"
        echo "  ./stop.sh                 # Arrêter"
        echo "  ./update.sh               # Mettre à jour"
    fi
    
    echo ""
    log_info "URLs d'accès:"
    echo "  🌐 Application: http://localhost:3000"
    echo "  🔌 API Backend: http://localhost:8001"
    echo "  📊 MongoDB: localhost:27017"
    echo ""
    log_info "Identifiants par défaut:"
    echo "  👤 Utilisateur: admin"
    echo "  🔑 Mot de passe: admin"
    echo ""
    log_warning "Changez le mot de passe admin en production!"
    echo ""
    log_info "📖 Documentation: README.md"
    log_info "🔧 Configuration: config.ini"
    echo ""
    log_success "Bonne utilisation de PromptAchat! 🚀"
}

# Run main function
main "$@"