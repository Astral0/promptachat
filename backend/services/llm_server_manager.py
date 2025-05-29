import asyncio
import time
from typing import Dict, List, Optional
import aiohttp
import logging
from datetime import datetime

from ..config import config
from ..models import LLMServerConfig, LLMServerTest

logger = logging.getLogger(__name__)

class LLMServerManager:
    """Service pour gérer les serveurs LLM multiples."""
    
    def __init__(self):
        self.servers: Dict[str, LLMServerConfig] = {}
        self._load_servers()
    
    def _load_servers(self):
        """Charge les serveurs LLM depuis la configuration."""
        # Configuration legacy (compatibilité)
        self._load_legacy_servers()
        
        # Nouvelle configuration multi-serveurs
        if config.config.has_section('llm_servers'):
            for server_name, server_config in config.config.items('llm_servers'):
                if server_name.startswith('#'):
                    continue
                    
                try:
                    parts = server_config.split(':')
                    if len(parts) >= 4:
                        server_type = parts[0]
                        url = parts[1] + ':' + parts[2] if parts[2] else parts[1]
                        api_key = parts[3] if parts[3] != 'none' else None
                        default_model = parts[4] if len(parts) > 4 else 'default'
                        
                        self.servers[server_name] = LLMServerConfig(
                            name=server_name,
                            type=server_type,
                            url=url,
                            api_key=api_key,
                            default_model=default_model
                        )
                        logger.info(f"Loaded LLM server: {server_name} ({server_type})")
                except Exception as e:
                    logger.error(f"Error parsing server config for {server_name}: {e}")
    
    def _load_legacy_servers(self):
        """Charge les serveurs depuis l'ancienne configuration."""
        # Ollama
        if config.getboolean('ollama', 'enabled', False):
            self.servers['ollama_legacy'] = LLMServerConfig(
                name='ollama_legacy',
                type='ollama',
                url=config.get('ollama', 'url', 'http://localhost:11434/v1'),
                api_key=None,
                default_model=config.get('ollama', 'default_model', 'llama3')
            )
        
        # Serveur interne
        internal_url = config.get('internal', 'url')
        if internal_url:
            self.servers['internal_legacy'] = LLMServerConfig(
                name='internal_legacy',
                type='openai',
                url=internal_url,
                api_key=config.get('internal', 'api_key'),
                default_model=config.get('internal', 'default_model', 'default')
            )
    
    def get_servers(self) -> Dict[str, LLMServerConfig]:
        """Retourne tous les serveurs configurés."""
        return self.servers
    
    def get_server(self, server_name: str) -> Optional[LLMServerConfig]:
        """Retourne un serveur spécifique."""
        return self.servers.get(server_name)
    
    async def test_server(self, server_name: str) -> LLMServerTest:
        """Teste la connectivité d'un serveur LLM."""
        server = self.get_server(server_name)
        if not server:
            return LLMServerTest(
                server_name=server_name,
                status="error",
                message="Serveur non trouvé"
            )
        
        start_time = time.time()
        
        try:
            if server.type == 'ollama':
                return await self._test_ollama_server(server, start_time)
            elif server.type == 'openai':
                return await self._test_openai_server(server, start_time)
            else:
                return LLMServerTest(
                    server_name=server_name,
                    status="error",
                    message=f"Type de serveur non supporté: {server.type}"
                )
                
        except asyncio.TimeoutError:
            return LLMServerTest(
                server_name=server_name,
                status="timeout",
                message="Timeout lors de la connexion",
                response_time=time.time() - start_time
            )
        except Exception as e:
            return LLMServerTest(
                server_name=server_name,
                status="error",
                message=f"Erreur: {str(e)}",
                response_time=time.time() - start_time
            )
    
    async def _test_ollama_server(self, server: LLMServerConfig, start_time: float) -> LLMServerTest:
        """Teste un serveur Ollama."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Test de version (endpoint de santé)
            version_url = server.url.replace('/v1', '') + '/api/version'
            async with session.get(version_url) as response:
                if response.status == 200:
                    # Récupération des modèles
                    models_url = server.url.replace('/v1', '') + '/api/tags'
                    models = []
                    try:
                        async with session.get(models_url) as models_response:
                            if models_response.status == 200:
                                data = await models_response.json()
                                models = [model['name'] for model in data.get('models', [])]
                    except:
                        pass
                    
                    return LLMServerTest(
                        server_name=server.name,
                        status="success",
                        message="Connexion réussie",
                        response_time=time.time() - start_time,
                        available_models=models
                    )
                else:
                    return LLMServerTest(
                        server_name=server.name,
                        status="error",
                        message=f"Erreur HTTP {response.status}",
                        response_time=time.time() - start_time
                    )
    
    async def _test_openai_server(self, server: LLMServerConfig, start_time: float) -> LLMServerTest:
        """Teste un serveur compatible OpenAI."""
        headers = {
            'Content-Type': 'application/json'
        }
        if server.api_key:
            headers['Authorization'] = f'Bearer {server.api_key}'
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Test avec endpoint models
            models_url = f"{server.url}/models"
            async with session.get(models_url, headers=headers) as response:
                if response.status == 200:
                    models = []
                    try:
                        data = await response.json()
                        models = [model['id'] for model in data.get('data', [])]
                    except:
                        models = [server.default_model]
                    
                    return LLMServerTest(
                        server_name=server.name,
                        status="success",
                        message="Connexion réussie",
                        response_time=time.time() - start_time,
                        available_models=models
                    )
                else:
                    return LLMServerTest(
                        server_name=server.name,
                        status="error",
                        message=f"Erreur HTTP {response.status}",
                        response_time=time.time() - start_time
                    )
    
    async def get_models(self, server_name: str) -> List[str]:
        """Récupère la liste des modèles disponibles pour un serveur."""
        test_result = await self.test_server(server_name)
        if test_result.status == "success":
            return test_result.available_models
        return []
    
    async def test_all_servers(self) -> Dict[str, LLMServerTest]:
        """Teste tous les serveurs configurés."""
        results = {}
        tasks = []
        
        for server_name in self.servers.keys():
            tasks.append(self.test_server(server_name))
        
        if tasks:
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, server_name in enumerate(self.servers.keys()):
                result = test_results[i]
                if isinstance(result, Exception):
                    results[server_name] = LLMServerTest(
                        server_name=server_name,
                        status="error",
                        message=f"Exception: {str(result)}"
                    )
                else:
                    results[server_name] = result
        
        return results
    
    def get_available_servers(self) -> List[str]:
        """Retourne la liste des noms de serveurs disponibles."""
        return list(self.servers.keys())
    
    def get_default_server(self) -> Optional[str]:
        """Retourne le nom du serveur par défaut."""
        if 'server1' in self.servers:
            return 'server1'
        elif self.servers:
            return list(self.servers.keys())[0]
        return None