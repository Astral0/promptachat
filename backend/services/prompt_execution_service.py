"""
Service pour l'exécution avancée de prompts avec toutes les fonctionnalités demandées.
"""
import json
import uuid
import time
import re
import base64
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path

import PyPDF2
import io

from backend.models import (
    PromptVariable, PromptExecutionRequest, PromptExecutionLog, 
    PromptExecutionResult
)
from backend.services.cockpit_service import CockpitService

class PromptExecutionService:
    """Service for advanced prompt execution with all requested features."""
    
    def __init__(self):
        """Initialize the service."""
        self.cockpit_service = CockpitService()
        self.executions = {}  # In-memory storage for execution results
    
    def extract_variables_from_content(self, content: str) -> List[str]:
        """Extract all variables {variable_name} from prompt content."""
        pattern = r'\{([^}]+)\}'
        return list(set(re.findall(pattern, content)))
    
    def validate_variables(self, content: str, variables: List[PromptVariable]) -> Dict[str, Any]:
        """Validate that all required variables are provided."""
        required_vars = self.extract_variables_from_content(content)
        provided_vars = {var.name for var in variables}
        missing_vars = [var for var in required_vars if var not in provided_vars]
        
        return {
            "is_valid": len(missing_vars) == 0,
            "missing_variables": missing_vars,
            "required_variables": required_vars,
            "provided_variables": list(provided_vars)
        }
    
    def substitute_variables(self, content: str, variables: List[PromptVariable]) -> str:
        """Substitute variables in the prompt content."""
        result = content
        
        for variable in variables:
            placeholder = f"{{{variable.name}}}"
            result = result.replace(placeholder, variable.value)
        
        return result
    
    def process_pdf_file(self, file_base64: str) -> str:
        """Convert PDF file to text."""
        try:
            # Decode base64
            file_data = base64.b64decode(file_base64)
            
            # Read PDF
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            return f"[Erreur lors du traitement du PDF: {str(e)}]"
    
    def build_final_prompt(
        self, 
        content: str, 
        variables: List[PromptVariable], 
        files: List[str] = None
    ) -> tuple[str, List[PromptExecutionLog]]:
        """Build the final prompt with variables and files."""
        logs = []
        
        # Log variable substitution
        if variables:
            logs.append(PromptExecutionLog(
                timestamp=datetime.utcnow(),
                action="variable_substitution",
                details=f"Substitution de {len(variables)} variables: {[v.name for v in variables]}",
                success=True
            ))
        
        # Substitute variables
        final_content = self.substitute_variables(content, variables)
        
        # Process files if any
        if files:
            logs.append(PromptExecutionLog(
                timestamp=datetime.utcnow(),
                action="file_processing",
                details=f"Traitement de {len(files)} fichier(s) PDF",
                success=True
            ))
            
            for i, file_base64 in enumerate(files):
                file_text = self.process_pdf_file(file_base64)
                final_content += f"\n\n--- FICHIER {i+1} ---\n{file_text}\n--- FIN FICHIER {i+1} ---"
        
        return final_content, logs
    
    async def execute_with_llm(
        self,
        final_prompt: str,
        server_config: Dict[str, Any],
        model: str
    ) -> tuple[str, List[PromptExecutionLog]]:
        """Execute the prompt with the specified LLM server."""
        logs = []
        start_time = time.time()
        
        try:
            logs.append(PromptExecutionLog(
                timestamp=datetime.utcnow(),
                action="api_call",
                details=f"Appel API vers {server_config['url']} avec le modèle {model}",
                success=True
            ))
            
            if server_config['type'].lower() == "ollama":
                # Ollama API call
                url = f"{server_config['url'].rstrip('/')}/api/generate"
                payload = {
                    "model": model,
                    "prompt": final_prompt,
                    "stream": False
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            result = data.get('response', '')
                            
                            logs.append(PromptExecutionLog(
                                timestamp=datetime.utcnow(),
                                action="response",
                                details=f"Réponse reçue en {time.time() - start_time:.2f}s",
                                success=True
                            ))
                            
                            return result, logs
                        else:
                            error_msg = f"Erreur HTTP {response.status}"
                            logs.append(PromptExecutionLog(
                                timestamp=datetime.utcnow(),
                                action="response",
                                details=error_msg,
                                success=False
                            ))
                            return f"Erreur: {error_msg}", logs
            
            else:  # OpenAI compatible
                # OpenAI API call
                url = f"{server_config['url'].rstrip('/')}/v1/chat/completions"
                headers = {}
                
                if server_config.get('api_key'):
                    headers["Authorization"] = f"Bearer {server_config['api_key']}"
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": final_prompt}
                    ],
                    "stream": False
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            result = data['choices'][0]['message']['content']
                            
                            logs.append(PromptExecutionLog(
                                timestamp=datetime.utcnow(),
                                action="response",
                                details=f"Réponse reçue en {time.time() - start_time:.2f}s",
                                success=True
                            ))
                            
                            return result, logs
                        else:
                            error_msg = f"Erreur HTTP {response.status}"
                            logs.append(PromptExecutionLog(
                                timestamp=datetime.utcnow(),
                                action="response",
                                details=error_msg,
                                success=False
                            ))
                            return f"Erreur: {error_msg}", logs
        
        except Exception as e:
            error_msg = f"Erreur lors de l'appel API: {str(e)}"
            logs.append(PromptExecutionLog(
                timestamp=datetime.utcnow(),
                action="response",
                details=error_msg,
                success=False
            ))
            return f"Erreur: {error_msg}", logs
    
    async def execute_prompt_streaming(
        self,
        final_prompt: str,
        server_config: Dict[str, Any],
        model: str
    ) -> AsyncGenerator[str, None]:
        """Execute the prompt with streaming response."""
        try:
            if server_config['type'].lower() == "ollama":
                # Ollama streaming API call
                url = f"{server_config['url'].rstrip('/')}/api/generate"
                payload = {
                    "model": model,
                    "prompt": final_prompt,
                    "stream": True
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            async for line in response.content:
                                if line:
                                    try:
                                        data = json.loads(line.decode('utf-8'))
                                        if 'response' in data:
                                            yield data['response']
                                    except json.JSONDecodeError:
                                        continue
                        else:
                            yield f"Erreur HTTP {response.status}"
            
            else:  # OpenAI compatible streaming
                url = f"{server_config['url'].rstrip('/')}/v1/chat/completions"
                headers = {}
                
                if server_config.get('api_key'):
                    headers["Authorization"] = f"Bearer {server_config['api_key']}"
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": final_prompt}
                    ],
                    "stream": True
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            async for line in response.content:
                                if line:
                                    line_str = line.decode('utf-8').strip()
                                    if line_str.startswith('data: '):
                                        data_str = line_str[6:]
                                        if data_str != '[DONE]':
                                            try:
                                                data = json.loads(data_str)
                                                if 'choices' in data and data['choices']:
                                                    delta = data['choices'][0].get('delta', {})
                                                    if 'content' in delta:
                                                        yield delta['content']
                                            except json.JSONDecodeError:
                                                continue
                        else:
                            yield f"Erreur HTTP {response.status}"
                            
        except Exception as e:
            yield f"Erreur lors de l'appel API: {str(e)}"
    
    async def execute_prompt(
        self,
        request: PromptExecutionRequest,
        prompt_content: str,
        server_config: Dict[str, Any]
    ) -> PromptExecutionResult:
        """Execute a prompt with full logging and processing."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Use modified content if provided, otherwise use original
        content = request.modified_content or prompt_content
        
        # Build final prompt
        final_prompt, logs = self.build_final_prompt(
            content, 
            request.variables, 
            request.files
        )
        
        # Determine model to use
        model = request.model or server_config.get('default_model', 'llama3')
        
        # Execute with LLM
        result, execution_logs = await self.execute_with_llm(
            final_prompt,
            server_config,
            model
        )
        
        # Combine all logs
        all_logs = logs + execution_logs
        
        # Create execution result
        execution_result = PromptExecutionResult(
            execution_id=execution_id,
            prompt_id=request.prompt_id,
            final_prompt=final_prompt,
            result=result,
            logs=all_logs,
            execution_time=time.time() - start_time
        )
        
        # Store execution result
        self.executions[execution_id] = execution_result
        
        return execution_result
    
    def get_execution_result(self, execution_id: str) -> Optional[PromptExecutionResult]:
        """Get execution result by ID."""
        return self.executions.get(execution_id)