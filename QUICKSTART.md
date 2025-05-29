# 🚀 Démarrage Rapide PromptAchat

## Installation en 3 Étapes

### 1️⃣ **Docker (Recommandé - 5 minutes)**

```bash
# Cloner le projet
git clone <votre-repo>
cd promptachat

# Démarrer avec Docker
docker-compose up -d

# ✅ C'est tout ! L'application est prête
```

**Accès :** http://localhost:3000 (admin/admin)

---

### 2️⃣ **Script Automatisé (Linux/macOS)**

```bash
# Cloner et installer
git clone <votre-repo>
cd promptachat
chmod +x install.sh
./install.sh

# Démarrer
./start.sh
```

---

### 3️⃣ **Windows PowerShell**

```powershell
# PowerShell en Administrateur
git clone <votre-repo>
cd promptachat
.\install.ps1

# Démarrer
.\start.bat
```

---

## 🎯 URLs Importantes

- **🌐 Application :** http://localhost:3000
- **🔌 API :** http://localhost:8001
- **📖 Documentation :** http://localhost:8001/docs
- **👤 Connexion :** admin / admin

## ⚡ Commandes Utiles

```bash
# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Statut
docker-compose ps
```

## 🔧 Configuration Rapide

### Ajouter un serveur LLM

Éditez `config.ini` :

```ini
[llm_servers]
# Ollama local
ollama = ollama|http://localhost:11434|none|llama3

# OpenAI (avec votre clé)
openai = openai|https://api.openai.com/v1|sk-your-key|gpt-4

# Serveur interne
internal = openai|http://votre-serveur:8080/v1|token|llama3
```

### Installer Ollama

```bash
# Installation
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger un modèle
ollama pull llama3

# Démarrer
ollama serve
```

## 🆘 Problèmes Courants

**Port déjà utilisé :**
```bash
docker-compose down
sudo lsof -i :3000 :8001 :27017
```

**Permissions Docker :**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Problème Windows :**
- Activer WSL2
- Redémarrer Docker Desktop

## 📱 Test Rapide

1. ✅ Ouvrir http://localhost:3000
2. ✅ Se connecter avec admin/admin
3. ✅ Aller dans "Bibliothèque"
4. ✅ Tester un prompt externe
5. ✅ Aller dans "Paramètres" pour configurer les serveurs LLM

## 🎉 Prêt !

Votre application PromptAchat est maintenant opérationnelle !

**Next Steps :**
- Configurer vos serveurs LLM
- Changer le mot de passe admin
- Créer vos premiers prompts

**Documentation complète :** [README.md](README.md) | [INSTALLATION.md](INSTALLATION.md)