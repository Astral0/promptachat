"""
Service pour la gestion des serveurs LLM utilisateur.
"""
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.models import UserLLMServer, UserLLMServerCreate, UserLLMServerUpdate
from backend.config import config

class UserLLMServerService:
    """Service for managing user LLM servers."""
    
    def __init__(self):
        """Initialize the service."""
        self.data_dir = Path(config.get('storage', 'data_directory', fallback='data'))
        self.servers_file = self.data_dir / 'user_llm_servers.json'
        self.data_dir.mkdir(exist_ok=True)
        self._load_servers()
    
    def _load_servers(self):
        """Load user LLM servers from file."""
        if self.servers_file.exists():
            try:
                with open(self.servers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.servers = {
                    server_id: UserLLMServer(**server_data)
                    for server_id, server_data in data.items()
                }
            except Exception as e:
                print(f"Error loading user LLM servers: {e}")
                self.servers = {}
        else:
            self.servers = {}
    
    def _save_servers(self):
        """Save user LLM servers to file."""
        try:
            data = {
                server_id: server.dict()
                for server_id, server in self.servers.items()
            }
            
            # Convert datetime objects to ISO format strings
            for server_data in data.values():
                if 'created_at' in server_data and isinstance(server_data['created_at'], datetime):
                    server_data['created_at'] = server_data['created_at'].isoformat()
                if 'updated_at' in server_data and isinstance(server_data['updated_at'], datetime):
                    server_data['updated_at'] = server_data['updated_at'].isoformat()
            
            with open(self.servers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user LLM servers: {e}")
    
    def create_server(self, user_id: str, server_data: UserLLMServerCreate) -> UserLLMServer:
        """Create a new user LLM server."""
        server = UserLLMServer(
            user_id=user_id,
            **server_data.dict()
        )
        
        self.servers[server.id] = server
        self._save_servers()
        return server
    
    def get_user_servers(self, user_id: str) -> List[UserLLMServer]:
        """Get all LLM servers for a user."""
        return [
            server for server in self.servers.values()
            if server.user_id == user_id and server.is_active
        ]
    
    def get_server(self, server_id: str, user_id: str) -> Optional[UserLLMServer]:
        """Get a specific server by ID if it belongs to the user."""
        server = self.servers.get(server_id)
        if server and server.user_id == user_id:
            return server
        return None
    
    def update_server(self, server_id: str, user_id: str, updates: UserLLMServerUpdate) -> Optional[UserLLMServer]:
        """Update a user LLM server."""
        server = self.get_server(server_id, user_id)
        if not server:
            return None
        
        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(server, field, value)
        
        server.updated_at = datetime.utcnow()
        self.servers[server_id] = server
        self._save_servers()
        return server
    
    def delete_server(self, server_id: str, user_id: str) -> bool:
        """Delete a user LLM server."""
        server = self.get_server(server_id, user_id)
        if not server:
            return False
        
        # Soft delete by setting is_active to False
        server.is_active = False
        server.updated_at = datetime.utcnow()
        self.servers[server_id] = server
        self._save_servers()
        return True
    
    def test_server_connection(self, server: UserLLMServer) -> Dict[str, Any]:
        """Test connection to a user LLM server."""
        import aiohttp
        import asyncio
        import time
        
        async def _test_connection():
            start_time = time.time()
            
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                
                if server.type.lower() == "ollama":
                    # Test Ollama server
                    url = f"{server.url.rstrip('/')}/api/tags"
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url) as response:
                            response_time = time.time() - start_time
                            
                            if response.status == 200:
                                data = await response.json()
                                models = [model['name'] for model in data.get('models', [])]
                                return {
                                    "status": "success",
                                    "message": "Connexion réussie",
                                    "response_time": response_time,
                                    "available_models": models
                                }
                            else:
                                return {
                                    "status": "error",
                                    "message": f"Erreur HTTP {response.status}",
                                    "response_time": response_time,
                                    "available_models": []
                                }
                
                else:  # OpenAI compatible
                    # Test OpenAI compatible server
                    url = f"{server.url.rstrip('/')}/v1/models"
                    headers = {}
                    
                    if server.api_key:
                        headers["Authorization"] = f"Bearer {server.api_key}"
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url, headers=headers) as response:
                            response_time = time.time() - start_time
                            
                            if response.status == 200:
                                data = await response.json()
                                models = [model['id'] for model in data.get('data', [])]
                                return {
                                    "status": "success",
                                    "message": "Connexion réussie",
                                    "response_time": response_time,
                                    "available_models": models
                                }
                            else:
                                return {
                                    "status": "error",
                                    "message": f"Erreur HTTP {response.status}",
                                    "response_time": response_time,
                                    "available_models": []
                                }
                                
            except asyncio.TimeoutError:
                return {
                    "status": "timeout",
                    "message": "Timeout de connexion",
                    "response_time": time.time() - start_time,
                    "available_models": []
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Erreur de connexion: {str(e)}",
                    "response_time": time.time() - start_time,
                    "available_models": []
                }
        
        # Run the async function
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_test_connection())
        except RuntimeError:
            # If no event loop is running, create a new one
            return asyncio.run(_test_connection())
    
    def get_all_available_servers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all available servers (system + user) for a user."""
        # Import here to avoid circular imports
        from backend.services.llm_server_manager import LLMServerManager
        
        all_servers = []
        
        # Add system servers
        system_manager = LLMServerManager()
        system_servers = system_manager.get_all_servers()
        
        for name, server in system_servers.items():
            all_servers.append({
                "id": f"system_{name}",
                "name": f"{name} (Système)",
                "type": server.type,
                "url": server.url,
                "default_model": server.default_model,
                "is_system": True,
                "is_available": server.is_available
            })
        
        # Add user servers
        user_servers = self.get_user_servers(user_id)
        for server in user_servers:
            all_servers.append({
                "id": server.id,
                "name": server.name,
                "type": server.type,
                "url": server.url,
                "default_model": server.default_model,
                "is_system": False,
                "is_available": True  # Assume user servers are available
            })
        
        return all_servers