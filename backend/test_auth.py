#!/usr/bin/env python3
"""
Script de test pour vérifier l'authentification.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.auth_service import AuthService

def test_auth():
    """Test l'authentification."""
    print("🔐 Test de l'authentification...")
    print("=" * 50)
    
    try:
        # Créer le service d'authentification
        auth_service = AuthService()
        
        # Vérifier l'existence de la base de données
        print(f"📁 Base de données: {auth_service.db_path}")
        print(f"   Existe: {'✅' if os.path.exists(auth_service.db_path) else '❌'}")
        
        # Lister les utilisateurs
        print(f"\n👥 Utilisateurs dans la base:")
        users = auth_service.list_users()
        if users:
            for user in users:
                status = "🟢 Actif" if user.is_active else "🔴 Inactif"
                print(f"   - {user.uid} ({user.full_name}) - {user.role.value} - {status}")
        else:
            print("   Aucun utilisateur trouvé")
        
        # Test de connexion avec admin/admin
        print(f"\n🔑 Test de connexion admin/admin...")
        user = auth_service.authenticate("admin", "admin")
        if user:
            print(f"   ✅ Connexion réussie!")
            print(f"   Utilisateur: {user.full_name} ({user.role.value})")
            
            # Créer un token
            token = auth_service.create_token(user)
            print(f"   🎫 Token généré: {token[:50]}...")
            
            # Vérifier le token
            payload = auth_service.verify_token(token)
            print(f"   ✅ Token vérifié: {payload['uid'] if payload else 'ERREUR'}")
        else:
            print(f"   ❌ Échec de la connexion")
        
        print(f"\n✅ Test d'authentification terminé!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1) 