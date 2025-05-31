import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
import os

from models import (
    SystemPrompt, UserPrompt, UserPromptCreate, UserPromptUpdate,
    PromptType
)
from config import config

logger = logging.getLogger(__name__)

class PromptService:
    """Service for managing system and user prompts."""
    
    def __init__(self):
        # Détection automatique de l'environnement
        self._setup_file_paths()
        self._ensure_user_prompts_file()
        
    def _setup_file_paths(self):
        """Configure les chemins des fichiers selon l'environnement (Docker vs Windows local)."""
        # Vérifier si on est dans un environnement Docker
        is_docker = (
            os.path.exists('/app/config.ini') or 
            os.environ.get('DOCKER_ENV') == 'true' or
            os.path.exists('/.dockerenv')
        )
        
        if is_docker:
            # Chemins Docker
            self.system_prompts_file = '/app/prompts.json'
            self.user_prompts_file = '/app/user_prompts.json'
            logger.info("PromptService configuré pour l'environnement Docker")
        else:
            # Chemins pour environnement local (Windows/Linux)
            # Le backend tourne depuis backend/, donc remonter d'un niveau
            project_root = Path(__file__).parent.parent.parent
            self.system_prompts_file = str(project_root / 'prompts.json')
            self.user_prompts_file = str(project_root / 'user_prompts.json')
            logger.info(f"PromptService configuré pour l'environnement local")
            logger.info(f"Fichier système: {self.system_prompts_file}")
            logger.info(f"Fichier utilisateur: {self.user_prompts_file}")
    
    def _ensure_user_prompts_file(self):
        """Ensure user prompts file exists."""
        if not Path(self.user_prompts_file).exists():
            with open(self.user_prompts_file, 'w') as f:
                json.dump({"internal": [], "external": []}, f, indent=2)
    
    def _load_system_prompts(self) -> Dict[str, List[SystemPrompt]]:
        """Load system prompts from JSON file."""
        try:
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            prompts = {}
            for prompt_type in ['internal', 'external']:
                prompts[prompt_type] = [
                    SystemPrompt(
                        id=prompt['id'],
                        type=PromptType(prompt_type),
                        **{k: v for k, v in prompt.items() if k != 'id'}
                    )
                    for prompt in data.get(prompt_type, [])
                ]
            
            return prompts
        except Exception as e:
            logger.error(f"Error loading system prompts: {e}")
            return {"internal": [], "external": []}
    
    def _load_user_prompts(self) -> Dict[str, List[UserPrompt]]:
        """Load user prompts from JSON file."""
        try:
            with open(self.user_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            prompts = {}
            for prompt_type in ['internal', 'external']:
                prompts[prompt_type] = [
                    UserPrompt(
                        type=PromptType(prompt_type),
                        **prompt
                    )
                    for prompt in data.get(prompt_type, [])
                ]
            
            return prompts
        except Exception as e:
            logger.error(f"Error loading user prompts: {e}")
            return {"internal": [], "external": []}
    
    def _save_user_prompts(self, prompts: Dict[str, List[UserPrompt]]):
        """Save user prompts to JSON file."""
        try:
            data = {}
            for prompt_type, prompt_list in prompts.items():
                data[prompt_type] = [
                    prompt.dict(exclude={'type'}) for prompt in prompt_list
                ]
            
            with open(self.user_prompts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Error saving user prompts: {e}")
            raise
    
    def get_all_prompts(self, user_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get all prompts (system + user's own + public user prompts)."""
        system_prompts = self._load_system_prompts()
        user_prompts = self._load_user_prompts()
        
        result = {}
        
        for prompt_type in ['internal', 'external']:
            result[prompt_type] = []
            
            # Add system prompts
            for prompt in system_prompts.get(prompt_type, []):
                result[prompt_type].append({
                    **prompt.dict(),
                    'source': 'system',
                    'editable': False
                })
            
            # Add user prompts
            for prompt in user_prompts.get(prompt_type, []):
                # Include if public or if it's the user's own prompt
                if prompt.is_public or (user_id and prompt.created_by == user_id):
                    result[prompt_type].append({
                        **prompt.dict(),
                        'source': 'user',
                        'editable': user_id == prompt.created_by
                    })
        
        return result
    
    def get_prompt_by_id(self, prompt_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get specific prompt by ID."""
        # Check system prompts first
        system_prompts = self._load_system_prompts()
        for prompt_type in ['internal', 'external']:
            for prompt in system_prompts.get(prompt_type, []):
                if prompt.id == prompt_id:
                    return {
                        **prompt.dict(),
                        'source': 'system',
                        'editable': False
                    }
        
        # Check user prompts
        user_prompts = self._load_user_prompts()
        for prompt_type in ['internal', 'external']:
            for prompt in user_prompts.get(prompt_type, []):
                if prompt.id == prompt_id:
                    # Check access permissions
                    if prompt.is_public or (user_id and prompt.created_by == user_id):
                        return {
                            **prompt.dict(),
                            'source': 'user',
                            'editable': user_id == prompt.created_by
                        }
        
        return None
    
    def create_user_prompt(self, prompt_data: UserPromptCreate, user_id: str) -> UserPrompt:
        """Create new user prompt."""
        # Load existing prompts
        user_prompts = self._load_user_prompts()
        
        # Create new prompt
        new_prompt = UserPrompt(
            id=str(uuid.uuid4()),
            created_by=user_id,
            **prompt_data.dict()
        )
        
        # Add to appropriate list
        prompt_type = new_prompt.type.value
        if prompt_type not in user_prompts:
            user_prompts[prompt_type] = []
        
        user_prompts[prompt_type].append(new_prompt)
        
        # Save to file
        self._save_user_prompts(user_prompts)
        
        return new_prompt
    
    def update_user_prompt(self, prompt_id: str, prompt_data: UserPromptUpdate, 
                          user_id: str) -> Optional[UserPrompt]:
        """Update existing user prompt."""
        user_prompts = self._load_user_prompts()
        
        # Find and update prompt
        for prompt_type in ['internal', 'external']:
            for i, prompt in enumerate(user_prompts.get(prompt_type, [])):
                if prompt.id == prompt_id and prompt.created_by == user_id:
                    # Update fields
                    update_data = prompt_data.dict(exclude_unset=True)
                    for field, value in update_data.items():
                        setattr(prompt, field, value)
                    
                    prompt.updated_at = datetime.utcnow()
                    
                    # Save changes
                    self._save_user_prompts(user_prompts)
                    
                    return prompt
        
        return None
    
    def delete_user_prompt(self, prompt_id: str, user_id: str) -> bool:
        """Delete user prompt."""
        user_prompts = self._load_user_prompts()
        
        # Find and remove prompt
        for prompt_type in ['internal', 'external']:
            prompts_list = user_prompts.get(prompt_type, [])
            for i, prompt in enumerate(prompts_list):
                if prompt.id == prompt_id and prompt.created_by == user_id:
                    prompts_list.pop(i)
                    self._save_user_prompts(user_prompts)
                    return True
        
        return False
    
    def duplicate_prompt(self, prompt_id: str, user_id: str, 
                        new_title: Optional[str] = None) -> Optional[UserPrompt]:
        """Duplicate an existing prompt (system or user) as a new user prompt."""
        original_prompt = self.get_prompt_by_id(prompt_id, user_id)
        if not original_prompt:
            return None
        
        # Create new prompt data
        prompt_data = UserPromptCreate(
            title=new_title or f"Copie de {original_prompt['title']}",
            content=original_prompt['content'],
            variables=original_prompt['variables'],
            accepts_files=original_prompt['accepts_files'],
            needs_cockpit=original_prompt['needs_cockpit'],
            category=original_prompt['category'],
            welcome_page_html=original_prompt['welcome_page_html'],
            type=PromptType(original_prompt['type']),
            based_on_system_prompt=prompt_id if original_prompt['source'] == 'system' else None
        )
        
        return self.create_user_prompt(prompt_data, user_id)
    
    def get_user_prompts(self, user_id: str) -> List[UserPrompt]:
        """Get all prompts created by a specific user."""
        user_prompts = self._load_user_prompts()
        
        result = []
        for prompt_type in ['internal', 'external']:
            for prompt in user_prompts.get(prompt_type, []):
                if prompt.created_by == user_id:
                    result.append(prompt)
        
        return result
    
    def get_categories(self) -> List[str]:
        """Get all unique categories from system and user prompts."""
        categories = set()
        
        # System prompts
        system_prompts = self._load_system_prompts()
        for prompt_type in ['internal', 'external']:
            for prompt in system_prompts.get(prompt_type, []):
                categories.add(prompt.category)
        
        # User prompts
        user_prompts = self._load_user_prompts()
        for prompt_type in ['internal', 'external']:
            for prompt in user_prompts.get(prompt_type, []):
                categories.add(prompt.category)
        
        return sorted(list(categories))
    
    def search_prompts(self, query: str, user_id: Optional[str] = None, 
                      category: Optional[str] = None, 
                      prompt_type: Optional[PromptType] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search prompts by title, content, or category."""
        all_prompts = self.get_all_prompts(user_id)
        
        result = {"internal": [], "external": []}
        
        for ptype in ['internal', 'external']:
            if prompt_type and ptype != prompt_type.value:
                continue
                
            for prompt in all_prompts.get(ptype, []):
                # Filter by category
                if category and prompt.get('category') != category:
                    continue
                
                # Search in title and content
                query_lower = query.lower()
                if (query_lower in prompt.get('title', '').lower() or 
                    query_lower in prompt.get('content', '').lower() or
                    query_lower in prompt.get('category', '').lower()):
                    result[ptype].append(prompt)
        
        return result
