# Makefile pour PromptAchat
# Simplifie les commandes Docker et de développement

.PHONY: help install start stop restart logs clean build test backup restore

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = promptachat

# Couleurs pour l'affichage
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)PromptAchat - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Exemples:$(NC)"
	@echo "  make install    # Installation complète"
	@echo "  make start      # Démarrer l'application"
	@echo "  make logs       # Voir les logs"
	@echo "  make stop       # Arrêter l'application"

install: ## Installation complète avec Docker
	@echo "$(BLUE)🚀 Installation PromptAchat...$(NC)"
	@chmod +x install.sh
	@./install.sh

setup: ## Configuration initiale (copie des fichiers template)
	@echo "$(BLUE)📋 Configuration initiale...$(NC)"
	@if [ ! -f config.ini ]; then cp config.ini.template config.ini; echo "$(GREEN)✅ config.ini créé$(NC)"; fi
	@if [ ! -f user_prompts.json ]; then echo '{"internal": [], "external": []}' > user_prompts.json; echo "$(GREEN)✅ user_prompts.json créé$(NC)"; fi

build: setup ## Construction des images Docker
	@echo "$(BLUE)🔨 Construction des images Docker...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build

start: ## Démarrer l'application (Docker)
	@echo "$(BLUE)🚀 Démarrage PromptAchat...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Application démarrée!$(NC)"
	@echo ""
	@echo "$(BLUE)📡 URLs d'accès:$(NC)"
	@echo "  🌐 Frontend: http://localhost:3000"
	@echo "  🔌 Backend:  http://localhost:8001"
	@echo "  📊 MongoDB:  localhost:27017"
	@echo ""
	@echo "$(BLUE)👤 Connexion par défaut:$(NC)"
	@echo "  Utilisateur: admin"
	@echo "  Mot de passe: admin"

start-dev: ## Démarrer en mode développement
	@echo "$(BLUE)🛠️  Démarrage en mode développement...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) -f docker-compose.dev.yml up -d

start-prod: ## Démarrer en mode production (avec Nginx)
	@echo "$(BLUE)🏭 Démarrage en mode production...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --profile production up -d

stop: ## Arrêter l'application
	@echo "$(BLUE)🛑 Arrêt de l'application...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Application arrêtée$(NC)"

restart: stop start ## Redémarrer l'application

logs: ## Afficher les logs en temps réel
	@docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## Logs du backend uniquement
	@docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## Logs du frontend uniquement
	@docker-compose -f $(COMPOSE_FILE) logs -f frontend

logs-mongodb: ## Logs de MongoDB
	@docker-compose -f $(COMPOSE_FILE) logs -f mongodb

status: ## Statut des conteneurs
	@echo "$(BLUE)📊 Statut des services:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

health: ## Vérification de santé des services
	@echo "$(BLUE)🏥 Vérification de santé...$(NC)"
	@echo ""
	@echo "$(BLUE)Backend:$(NC)"
	@curl -s http://localhost:8001/api/health | jq . || echo "$(RED)❌ Backend inaccessible$(NC)"
	@echo ""
	@echo "$(BLUE)Frontend:$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000 || echo "$(RED)❌ Frontend inaccessible$(NC)"
	@echo ""
	@echo "$(BLUE)MongoDB:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongosh --eval "db.adminCommand('ping')" --quiet || echo "$(RED)❌ MongoDB inaccessible$(NC)"

shell-backend: ## Shell dans le conteneur backend
	@docker-compose -f $(COMPOSE_FILE) exec backend /bin/bash

shell-frontend: ## Shell dans le conteneur frontend
	@docker-compose -f $(COMPOSE_FILE) exec frontend /bin/sh

shell-mongodb: ## Shell MongoDB
	@docker-compose -f $(COMPOSE_FILE) exec mongodb mongosh

update: ## Mise à jour de l'application
	@echo "$(BLUE)🔄 Mise à jour PromptAchat...$(NC)"
	@git pull
	@docker-compose -f $(COMPOSE_FILE) build
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Mise à jour terminée$(NC)"

backup: ## Sauvegarde de la base de données
	@echo "$(BLUE)💾 Sauvegarde de la base de données...$(NC)"
	@mkdir -p backups
	@docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongodump --db promptachat_db --archive --gzip | gzip > backups/promptachat_backup_$(shell date +%Y%m%d_%H%M%S).gz
	@echo "$(GREEN)✅ Sauvegarde créée dans backups/$(NC)"

restore: ## Restaurer la base de données (nécessite BACKUP_FILE=path)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "$(RED)❌ Spécifiez BACKUP_FILE=path$(NC)"; exit 1; fi
	@echo "$(BLUE)🔄 Restauration depuis $(BACKUP_FILE)...$(NC)"
	@gunzip -c $(BACKUP_FILE) | docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongorestore --archive --gzip --drop
	@echo "$(GREEN)✅ Restauration terminée$(NC)"

clean: ## Nettoyage des conteneurs et volumes
	@echo "$(YELLOW)⚠️  Arrêt et suppression des conteneurs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(YELLOW)🧹 Nettoyage des images inutilisées...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-all: ## Nettoyage complet (ATTENTION: supprime les données)
	@echo "$(RED)⚠️  ATTENTION: Cette commande supprimera TOUTES les données!$(NC)"
	@read -p "Êtes-vous sûr ? [y/N] " confirm && [ "$$confirm" = "y" ]
	@docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	@docker volume prune -f
	@docker image prune -a -f
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

test: ## Exécuter les tests
	@echo "$(BLUE)🧪 Exécution des tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec backend python -m pytest tests/ -v
	@docker-compose -f $(COMPOSE_FILE) exec frontend yarn test --watchAll=false

install-ollama: ## Installer et configurer Ollama
	@echo "$(BLUE)🤖 Téléchargement du modèle Ollama...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec ollama ollama pull llama3
	@echo "$(GREEN)✅ Modèle llama3 installé$(NC)"

monitor: ## Surveillance des ressources
	@echo "$(BLUE)📊 Surveillance des ressources:$(NC)"
	@docker stats $(PROJECT_NAME)-mongodb $(PROJECT_NAME)-backend $(PROJECT_NAME)-frontend

dev-setup: ## Configuration pour le développement local
	@echo "$(BLUE)🛠️  Configuration développement...$(NC)"
	@cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@cd frontend && yarn install
	@echo "$(GREEN)✅ Environnement de développement prêt$(NC)"
	@echo ""
	@echo "$(BLUE)Pour démarrer en mode développement:$(NC)"
	@echo "  Terminal 1: cd backend && source venv/bin/activate && uvicorn server:app --reload"
	@echo "  Terminal 2: cd frontend && yarn start"

docs: ## Générer la documentation
	@echo "$(BLUE)📚 Génération de la documentation...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec backend python -c "import server; help(server)"

# Commandes par défaut
all: setup build start

# Si aucune commande n'est spécifiée, afficher l'aide
.DEFAULT_GOAL := help