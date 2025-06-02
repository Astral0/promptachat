"""
Service pour la gestion des serveurs LLM système par les administrateurs.
Les serveurs sont stockés dans le fichier config.ini et peuvent être modifiés via l'IHM.
"""
import configparser
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.models import LLMServerConfig

class AdminLLMServerService:
    """Service for managing system LLM servers by administrators."""
    
    def __init__(self):
        """Initialize the service."""
        self.config_file = Path('config.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        # Ensure llm_servers section exists
        if 'llm_servers' not in self.config:
            self.config.add_section('llm_servers')
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_all_servers(self) -> List[Dict[str, Any]]:
        """Get all system LLM servers."""
        servers = []
        
        if 'llm_servers' in self.config:
            for name, config_string in self.config['llm_servers'].items():
                try:
                    # Parse config string: type|url|api_key|model
                    parts = config_string.split('|')
                    if len(parts) >= 4:
                        servers.append({
                            "id": name,
                            "name": name,
                            "type": parts[0],
                            "url": parts[1],
                            "api_key": parts[2] if parts[2] != 'none' else None,
                            "default_model": parts[3],
                            "is_system": True,
                            "is_active": True
                        })
                except Exception as e:
                    print(f"Error parsing server config for {name}: {e}")
        
        return servers
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific system server."""
        servers = self.get_all_servers()
        return next((s for s in servers if s['id'] == server_id), None)
    
    def create_server(self, server_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new system LLM server."""
        name = server_data['name']
        server_type = server_data['type']
        url = server_data['url']
        api_key = server_data.get('api_key') or 'none'
        default_model = server_data['default_model']
        
        # Create config string: type|url|api_key|model
        config_string = f"{server_type}|{url}|{api_key}|{default_model}"
        
        # Add to config
        self.config.set('llm_servers', name, config_string)
        self._save_config()
        
        return {
            "id": name,
            "name": name,
            "type": server_type,
            "url": url,
            "api_key": api_key if api_key != 'none' else None,
            "default_model": default_model,
            "is_system": True,
            "is_active": True
        }
    
    def update_server(self, server_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a system LLM server."""
        # Get current server
        current_server = self.get_server(server_id)
        if not current_server:
            return None
        
        # Apply updates
        name = updates.get('name', current_server['name'])
        server_type = updates.get('type', current_server['type'])
        url = updates.get('url', current_server['url'])
        api_key = updates.get('api_key', current_server['api_key']) or 'none'
        default_model = updates.get('default_model', current_server['default_model'])
        
        # If name changed, remove old entry
        if name != server_id:
            self.config.remove_option('llm_servers', server_id)
        
        # Create config string: type|url|api_key|model
        config_string = f"{server_type}|{url}|{api_key}|{default_model}"
        
        # Update config
        self.config.set('llm_servers', name, config_string)
        self._save_config()
        
        return {
            "id": name,
            "name": name,
            "type": server_type,
            "url": url,
            "api_key": api_key if api_key != 'none' else None,
            "default_model": default_model,
            "is_system": True,
            "is_active": True
        }
    
    def delete_server(self, server_id: str) -> bool:
        """Delete a system LLM server."""
        if not self.config.has_option('llm_servers', server_id):
            return False
        
        self.config.remove_option('llm_servers', server_id)
        self._save_config()
        return True
    
    def test_server_connection(self, server_id: str) -> Dict[str, Any]:
        """Test connection to a system LLM server."""
        server = self.get_server(server_id)
        if not server:
            return {"status": "error", "message": "Serveur non trouvé"}
        
        import requests
        import time
        
        start_time = time.time()
        
        try:
            if server['type'].lower() == "ollama":
                # Test Ollama server
                url = f"{server['url'].rstrip('/')}/api/tags"
                
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
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
                        "message": f"Erreur HTTP {response.status_code}",
                        "response_time": response_time,
                        "available_models": []
                    }
            
            else:  # OpenAI compatible
                # Test OpenAI compatible server
                url = f"{server['url'].rstrip('/')}/v1/models"
                headers = {}
                
                if server['api_key']:
                    headers["Authorization"] = f"Bearer {server['api_key']}"
                
                response = requests.get(url, headers=headers, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
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
                        "message": f"Erreur HTTP {response.status_code}",
                        "response_time": response_time,
                        "available_models": []
                    }
                        
        except requests.exceptions.Timeout:
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