import asyncio
import json
import re
from typing import Dict, Any, Optional, AsyncGenerator, List
import aiohttp
import logging
from datetime import datetime

from ..config import get_llm_config, get_features_config
from ..models import LLMRequest, LLMResponse, ConfidentialityLevel
from .llm_server_manager import LLMServerManager

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with various LLM endpoints."""
    
    def __init__(self):
        self.llm_config = get_llm_config()
        self.features_config = get_features_config()
        self.server_manager = LLMServerManager()
        
    async def _make_openai_request(self, url: str, headers: Dict[str, str], 
                                  payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Make streaming request to OpenAI-compatible endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"LLM request failed: {response.status} - {error_text}")
                    yield f"Erreur: {response.status} - {error_text}"
                    return
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and json_data['choices']:
                                delta = json_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    async def chat_with_server(self, server_name: str, request: LLMRequest, 
                              model: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Chat with a specific LLM server."""
        server = self.server_manager.get_server(server_name)
        if not server:
            yield f"Erreur: Serveur {server_name} non trouvé"
            return
        
        # Utiliser le modèle spécifié ou le modèle par défaut du serveur
        selected_model = model or request.model or server.default_model
        
        if server.type == 'ollama':
            async for chunk in self._chat_ollama(server, request, selected_model):
                yield chunk
        elif server.type == 'openai':
            async for chunk in self._chat_openai(server, request, selected_model):
                yield chunk
        else:
            yield f"Erreur: Type de serveur {server.type} non supporté"

    async def _chat_ollama(self, server, request: LLMRequest, model: str) -> AsyncGenerator[str, None]:
        """Chat with Ollama server."""
        url = f"{server.url}/chat/completions"
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ],
            'temperature': request.temperature or self.llm_config['default_temperature'],
            'max_tokens': request.max_tokens or self.llm_config['max_tokens'],
            'stream': request.stream
        }
        
        logger.info(f"Making Ollama request to {url} with model {model}")
        
        try:
            async for chunk in self._make_openai_request(url, headers, payload):
                yield chunk
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            yield f"Erreur Ollama: {str(e)}"

    async def _chat_openai(self, server, request: LLMRequest, model: str) -> AsyncGenerator[str, None]:
        """Chat with OpenAI-compatible server."""
        url = f"{server.url}/chat/completions"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if server.api_key:
            headers['Authorization'] = f"Bearer {server.api_key}"
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ],
            'temperature': request.temperature or self.llm_config['default_temperature'],
            'max_tokens': request.max_tokens or self.llm_config['max_tokens'],
            'stream': request.stream
        }
        
        logger.info(f"Making OpenAI request to {url} with model {model}")
        
        try:
            async for chunk in self._make_openai_request(url, headers, payload):
                yield chunk
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            yield f"Erreur OpenAI: {str(e)}"

    # Méthodes legacy pour compatibilité
    async def chat_internal(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Chat with internal LLM (legacy method)."""
        default_server = self.server_manager.get_default_server()
        if default_server:
            async for chunk in self.chat_with_server(default_server, request):
                yield chunk
        else:
            yield "Erreur: Aucun serveur LLM configuré"

    async def chat_ollama(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Chat with Ollama (legacy method)."""
        # Chercher un serveur Ollama
        for server_name, server in self.server_manager.get_servers().items():
            if server.type == 'ollama':
                async for chunk in self.chat_with_server(server_name, request):
                    yield chunk
                return
        
        yield "Erreur: Aucun serveur Ollama configuré"

    async def generate_external_prompt(self, request: LLMRequest) -> str:
        """Generate prompt text for external LLM use."""
        # For external use, we just return the formatted prompt
        return request.prompt
    
    async def check_privacy(self, text: str) -> Dict[str, Any]:
        """Check confidentiality level of text using internal LLM."""
        if not self.features_config['enable_privacy_check']:
            return {
                'confidentiality_level': 'C0',
                'concerns': [],
                'recommendations': []
            }

        privacy_prompt = f"""
Analyse ce texte pour déterminer son niveau de confidentialité selon la classification suivante:
- C0: Information publique
- C1: Information interne (pas de données sensibles)
- C2: Information confidentielle (données sensibles, informations stratégiques)
- C3: Information secrète (données très sensibles, secrets commerciaux)

Réponds uniquement au format JSON:
{{
    "confidentiality_level": "C0|C1|C2|C3",
    "concerns": ["liste des préoccupations identifiées"],
    "recommendations": ["recommandations pour sécuriser l'information"]
}}

Texte à analyser:
{text[:2000]}  # Limite pour éviter les prompts trop longs
"""
        
        try:
            request = LLMRequest(prompt=privacy_prompt, stream=False)
            response_text = ""
            
            # Try default server
            default_server = self.server_manager.get_default_server()
            if default_server:
                async for chunk in self.chat_with_server(default_server, request):
                    response_text += chunk
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback analysis
                return self._basic_privacy_check(text)
                
        except Exception as e:
            logger.error(f"Privacy check failed: {e}")
            return self._basic_privacy_check(text)
    
    def _basic_privacy_check(self, text: str) -> Dict[str, Any]:
        """Basic regex-based privacy check as fallback."""
        text_lower = text.lower()
        
        # High risk patterns
        high_risk_patterns = [
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card numbers
            r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b',  # SSN-like numbers
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
            r'mot de passe|password|secret|confidentiel|privé'
        ]
        
        concerns = []
        confidentiality_level = 'C0'
        
        for pattern in high_risk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                concerns.append(f"Données potentiellement sensibles détectées: {pattern}")
                confidentiality_level = 'C2'
        
        # Check for internal information
        internal_keywords = ['edf', 'enedis', 'interne', 'stratégique', 'confidentiel']
        if any(keyword in text_lower for keyword in internal_keywords):
            if confidentiality_level == 'C0':
                confidentiality_level = 'C1'
            concerns.append("Informations internes détectées")
        
        recommendations = []
        if confidentiality_level != 'C0':
            recommendations.append("Réviser le contenu avant partage externe")
            recommendations.append("Vérifier la classification avec votre responsable")
        
        return {
            'confidentiality_level': confidentiality_level,
            'concerns': concerns,
            'recommendations': recommendations
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models for each LLM provider."""
        models = {}
        
        for server_name, server in self.server_manager.get_servers().items():
            models[server_name] = [server.default_model]
        
        return models
    
    async def get_server_models(self, server_name: str) -> List[str]:
        """Get available models for a specific server."""
        return await self.server_manager.get_models(server_name)
    
    def get_servers(self):
        """Get all configured servers."""
        return self.server_manager.get_servers()
    
    async def test_server(self, server_name: str):
        """Test a specific server."""
        return await self.server_manager.test_server(server_name)
    
    async def test_all_servers(self):
        """Test all configured servers."""
        return await self.server_manager.test_all_servers()
