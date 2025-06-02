"""
Service pour la gestion des catégories.
"""
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.models import Category, CategoryCreate, CategoryUpdate
from backend.config import config

class CategoryService:
    """Service for managing categories."""
    
    def __init__(self):
        """Initialize the service."""
        self.data_dir = Path(config.get('storage', 'data_directory', fallback='data'))
        self.categories_file = self.data_dir / 'categories.json'
        self.data_dir.mkdir(exist_ok=True)
        self._load_categories()
        self._ensure_default_categories()
    
    def _load_categories(self):
        """Load categories from file."""
        if self.categories_file.exists():
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.categories = {
                    cat_id: Category(**cat_data)
                    for cat_id, cat_data in data.items()
                }
            except Exception as e:
                print(f"Error loading categories: {e}")
                self.categories = {}
        else:
            self.categories = {}
    
    def _save_categories(self):
        """Save categories to file."""
        try:
            data = {
                cat_id: cat.dict()
                for cat_id, cat in self.categories.items()
            }
            
            # Convert datetime objects to ISO format strings
            for cat_data in data.values():
                if 'created_at' in cat_data and isinstance(cat_data['created_at'], datetime):
                    cat_data['created_at'] = cat_data['created_at'].isoformat()
            
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving categories: {e}")
    
    def _ensure_default_categories(self):
        """Ensure default system categories exist."""
        default_categories = [
            {
                "name": "Analyse Contractuelle",
                "description": "Prompts pour l'analyse et l'évaluation de contrats fournisseurs"
            },
            {
                "name": "Évaluation Fournisseur",
                "description": "Prompts pour évaluer les performances et la qualité des fournisseurs"
            },
            {
                "name": "Négociation",
                "description": "Prompts d'aide à la négociation et aux stratégies d'achat"
            },
            {
                "name": "Veille Marché",
                "description": "Prompts pour la surveillance et l'analyse des marchés"
            },
            {
                "name": "RSE et Développement Durable",
                "description": "Prompts liés à la responsabilité sociale et au développement durable"
            },
            {
                "name": "Conformité et Réglementation",
                "description": "Prompts pour la conformité réglementaire et les standards"
            },
            {
                "name": "Gestion des Risques",
                "description": "Prompts pour l'identification et la gestion des risques fournisseurs"
            },
            {
                "name": "Innovation et Technologie",
                "description": "Prompts pour identifier les innovations et nouvelles technologies"
            },
            {
                "name": "Reporting et Analyse",
                "description": "Prompts pour la création de rapports et l'analyse de données"
            },
            {
                "name": "Stratégie Achats",
                "description": "Prompts pour la stratégie et l'optimisation des achats"
            }
        ]
        
        # Check if any system categories exist
        has_system_categories = any(cat.is_system for cat in self.categories.values())
        
        if not has_system_categories:
            for cat_data in default_categories:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_system=True,
                    created_by=None
                )
                self.categories[category.id] = category
            
            self._save_categories()
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return list(self.categories.values())
    
    def get_categories_by_user(self, user_id: Optional[str] = None) -> List[Category]:
        """Get categories available to a user (system + user created)."""
        categories = []
        
        for category in self.categories.values():
            # System categories are available to everyone
            if category.is_system:
                categories.append(category)
            # User categories are only available to their creator
            elif category.created_by == user_id:
                categories.append(category)
        
        return categories
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        return self.categories.get(category_id)
    
    def create_category(self, category_data: CategoryCreate, user_id: str) -> Category:
        """Create a new user category."""
        category = Category(
            name=category_data.name,
            description=category_data.description,
            created_by=user_id,
            is_system=False
        )
        
        self.categories[category.id] = category
        self._save_categories()
        return category
    
    def update_category(self, category_id: str, updates: CategoryUpdate, user_id: str) -> Optional[Category]:
        """Update a category (only if created by user)."""
        category = self.categories.get(category_id)
        if not category or category.is_system or category.created_by != user_id:
            return None
        
        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.categories[category_id] = category
        self._save_categories()
        return category
    
    def delete_category(self, category_id: str, user_id: str) -> bool:
        """Delete a category (only if created by user)."""
        category = self.categories.get(category_id)
        if not category or category.is_system or category.created_by != user_id:
            return False
        
        del self.categories[category_id]
        self._save_categories()
        return True
    
    def get_categories_dict(self) -> Dict[str, str]:
        """Get categories as a dictionary of {id: name}."""
        return {
            cat_id: category.name
            for cat_id, category in self.categories.items()
        }
    
    def suggest_category_for_prompt(self, prompt_title: str, prompt_content: str) -> Optional[str]:
        """Suggest a category based on prompt content using keywords."""
        
        # Keywords for each category
        category_keywords = {
            "Analyse Contractuelle": [
                "contrat", "contractuel", "clause", "conditions", "accord",
                "engagement", "obligation", "responsabilité", "garantie"
            ],
            "Évaluation Fournisseur": [
                "fournisseur", "performance", "évaluation", "qualité", "livraison",
                "service", "satisfaction", "notation", "score"
            ],
            "Négociation": [
                "négociation", "prix", "tarif", "remise", "conditions commerciales",
                "offre", "proposition", "strategy", "tactique"
            ],
            "Veille Marché": [
                "marché", "concurrence", "benchmark", "prix marché", "tendance",
                "évolution", "analyse marché", "veille"
            ],
            "RSE et Développement Durable": [
                "rse", "développement durable", "environnement", "social",
                "éthique", "durable", "écologique", "responsable"
            ],
            "Conformité et Réglementation": [
                "conformité", "réglementation", "norme", "certification",
                "standard", "audit", "compliance", "règlement"
            ],
            "Gestion des Risques": [
                "risque", "sécurité", "continuité", "mitigation",
                "analyse risque", "évaluation risque", "prévention"
            ],
            "Innovation et Technologie": [
                "innovation", "technologie", "digital", "numérique",
                "transformation", "nouvelle technologie", "r&d"
            ],
            "Reporting et Analyse": [
                "rapport", "reporting", "analyse", "dashboard", "kpi",
                "indicateur", "métrique", "suivi", "tableau de bord"
            ],
            "Stratégie Achats": [
                "stratégie", "optimisation", "processus", "organisation",
                "amélioration", "efficiency", "transformation achats"
            ]
        }
        
        # Combine title and content for analysis
        text_to_analyze = f"{prompt_title} {prompt_content}".lower()
        
        # Score each category
        category_scores = {}
        for category_name, keywords in category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    score += 1
            
            if score > 0:
                category_scores[category_name] = score
        
        # Return the category with the highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            
            # Find the category ID by name
            for cat_id, category in self.categories.items():
                if category.name == best_category:
                    return cat_id
        
        return None