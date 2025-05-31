#!/usr/bin/env python3
"""
Script de test pour vérifier le chargement des prompts.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.prompt_service import PromptService

def test_prompt_loading():
    """Test le chargement des prompts."""
    print("🔍 Test du chargement des prompts...")
    print("=" * 50)
    
    try:
        # Créer le service
        service = PromptService()
        
        # Vérifier l'existence des fichiers
        print(f"📁 Fichier système: {service.system_prompts_file}")
        print(f"   Existe: {'✅' if os.path.exists(service.system_prompts_file) else '❌'}")
        
        print(f"📁 Fichier utilisateur: {service.user_prompts_file}")
        print(f"   Existe: {'✅' if os.path.exists(service.user_prompts_file) else '❌'}")
        
        print("\n🔄 Chargement des prompts...")
        
        # Charger tous les prompts
        all_prompts = service.get_all_prompts()
        
        # Afficher les résultats
        print(f"\n📊 Résultats:")
        print(f"   Prompts internes: {len(all_prompts.get('internal', []))}")
        print(f"   Prompts externes: {len(all_prompts.get('external', []))}")
        
        # Détail des prompts
        for prompt_type in ['internal', 'external']:
            prompts = all_prompts.get(prompt_type, [])
            if prompts:
                print(f"\n📋 Prompts {prompt_type}:")
                for i, prompt in enumerate(prompts, 1):
                    print(f"   {i}. {prompt.get('title', 'Sans titre')} (ID: {prompt.get('id', 'N/A')})")
        
        print(f"\n✅ Test réussi ! {len(all_prompts.get('internal', [])) + len(all_prompts.get('external', []))} prompts chargés au total.")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_prompt_loading()
    sys.exit(0 if success else 1) 