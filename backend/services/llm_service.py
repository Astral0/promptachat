import asyncio
import json
import re
from typing import Dict, Any, Optional, AsyncGenerator, List
import aiohttp
import logging
from datetime import datetime

from ..config import get_llm_config, get_features_config
from ..models import LLMRequest, LLMResponse, ConfidentialityLevel

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with various LLM endpoints."""
    
    def __init__(self):
        self.llm_config = get_llm_config()
        self.features_config = get_features_config()
        
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
    
    async def chat_internal(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Chat with internal LLM."""
        config = self.llm_config['internal']
        
        if not config['url']:
            yield "Erreur: URL du LLM interne non configurée"
            return
        
        url = f"{config['url']}/chat/completions"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if config['api_key']:
            headers['Authorization'] = f"Bearer {config['api_key']}"
        
        payload = {
            'model': request.model or config['default_model'],
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ],
            'temperature': request.temperature or self.llm_config['default_temperature'],
            'max_tokens': request.max_tokens or self.llm_config['max_tokens'],
            'stream': request.stream
        }
        
        logger.info(f"Making internal LLM request to {url}")
        
        async for chunk in self._make_openai_request(url, headers, payload):
            yield chunk
    
    async def chat_ollama(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Chat with Ollama."""
        config = self.llm_config['ollama']
        
        if not config['enabled']:
            yield "Erreur: Ollama est désactivé"
            return
        
        url = f"{config['url']}/chat/completions"
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': request.model or config['default_model'],
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ],
            'temperature': request.temperature or self.llm_config['default_temperature'],
            'max_tokens': request.max_tokens or self.llm_config['max_tokens'],
            'stream': request.stream
        }
        
        logger.info(f"Making Ollama request to {url}")
        
        try:
            async for chunk in self._make_openai_request(url, headers, payload):
                yield chunk
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            yield f"Erreur Ollama: {str(e)}"
    
    async def chat_oneapi(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Chat with OneAPI gateway."""
        config = self.llm_config['oneapi']
        
        if not config['use_oneapi']:
            yield "Erreur: OneAPI est désactivé"
            return
        
        url = f"{config['url']}/chat/completions"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if config['api_key']:
            headers['Authorization'] = f"Bearer {config['api_key']}"
        
        payload = {
            'model': request.model or self.llm_config['external']['default_model'],
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ],
            'temperature': request.temperature or self.llm_config['default_temperature'],
            'max_tokens': request.max_tokens or self.llm_config['max_tokens'],
            'stream': request.stream
        }
        
        logger.info(f"Making OneAPI request to {url}")
        
        async for chunk in self._make_openai_request(url, headers, payload):
            yield chunk
    
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
            
            # Try internal LLM first, then Ollama
            try:
                async for chunk in self.chat_internal(request):
                    response_text += chunk
            except:
                async for chunk in self.chat_ollama(request):
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
        models = {
            'internal': [],
            'ollama': [],
            'oneapi': []
        }
        
        # Add configured default models
        if self.llm_config['internal']['url']:
            models['internal'].append(self.llm_config['internal']['default_model'])
        
        if self.llm_config['ollama']['enabled']:
            models['ollama'].append(self.llm_config['ollama']['default_model'])
        
        if self.llm_config['oneapi']['use_oneapi']:
            models['oneapi'].append(self.llm_config['external']['default_model'])
        
        return models
    
    async def get_ollama_models(self) -> List[str]:
        """Get available Ollama models."""
        if not self.llm_config['ollama']['enabled']:
            return []
        
        try:
            url = f"{self.llm_config['ollama']['url']}/models"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
        
        return [self.llm_config['ollama']['default_model']]
