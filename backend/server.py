from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import PyPDF2
import io
import shutil

from backend.models import (
    User, UserLogin, Token, UserCreate, UserUpdate,
    UserPrompt, UserPromptCreate, UserPromptUpdate,
    ChatRequest, LLMRequest, PromptExecutionResult,
    LLMServerConfig, LLMServerTest, UserPreferences,
    UserLLMServer, UserLLMServerCreate, UserLLMServerUpdate,
    CockpitVariable, Category, CategoryCreate, CategoryUpdate,
    AdminLLMServerCreate, AdminLLMServerUpdate,
    PromptVariable, PromptExecutionRequest, PromptExecutionLog
)
from backend.services import AuthService, PromptService, LLMService
from backend.services.cockpit_service import CockpitService
from backend.services.user_llm_server_service import UserLLMServerService  
from backend.services.category_service import CategoryService
from backend.services.admin_llm_server_service import AdminLLMServerService
from backend.services.prompt_execution_service import PromptExecutionService
from backend.config import get_app_config, get_database_config

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize file storage directory
FILES_DIR = ROOT_DIR / "uploaded_files"
FILES_DIR.mkdir(exist_ok=True)

# Initialize services
auth_service = AuthService()
prompt_service = PromptService()
llm_service = LLMService()
cockpit_service = CockpitService()
user_llm_server_service = UserLLMServerService()
category_service = CategoryService()
admin_llm_server_service = AdminLLMServerService()
prompt_execution_service = PromptExecutionService()

# Create the main app
app = FastAPI(
    title="PromptAchat",
    description="Bibliothèque de prompts interactive pour la filière Achat",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    token_data = auth_service.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    user = auth_service.get_user_by_uid(token_data.get('uid'))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé ou inactif"
        )
    
    return user

# Optional authentication (for public endpoints)
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Admin user dependency
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    return current_user

# ===============================
# Authentication Routes
# ===============================

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """User login."""
    user = auth_service.authenticate(user_data.uid, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )
    
    access_token = auth_service.create_token(user)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@api_router.get("/auth/config")
async def get_auth_config():
    """Get authentication configuration."""
    app_config = get_app_config()
    return {
        "app_name": app_config["name"],
        "app_title": app_config["title"],
        "logo_url": app_config.get("logo_url"),
        "contact_email": app_config["contact_email"]
    }

# ===============================
# Prompt Management Routes
# ===============================

@api_router.get("/prompts")
async def get_prompts(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Get all available prompts."""
    user_id = current_user.id if current_user else None
    return prompt_service.get_all_prompts(user_id)

@api_router.get("/prompts/categories")
async def get_categories():
    """Get all prompt categories."""
    return prompt_service.get_categories()

@api_router.get("/prompts/search")
async def search_prompts(
    q: str,
    category: Optional[str] = None,
    type: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Search prompts."""
    user_id = current_user.id if current_user else None
    prompt_type = None
    if type in ['internal', 'external']:
        from backend.models import PromptType
        prompt_type = PromptType(type)
    
    return prompt_service.search_prompts(q, user_id, category, prompt_type)

@api_router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str, current_user: Optional[User] = Depends(get_current_user_optional)):
    """Get specific prompt by ID."""
    user_id = current_user.id if current_user else None
    prompt = prompt_service.get_prompt_by_id(prompt_id, user_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    return prompt

@api_router.post("/prompts", response_model=UserPrompt)
async def create_prompt(
    prompt_data: UserPromptCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new user prompt."""
    return prompt_service.create_user_prompt(prompt_data, current_user.id)

@api_router.put("/prompts/{prompt_id}", response_model=UserPrompt)
async def update_prompt(
    prompt_id: str,
    prompt_data: UserPromptUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user prompt."""
    updated_prompt = prompt_service.update_user_prompt(prompt_id, prompt_data, current_user.id)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé ou non autorisé")
    return updated_prompt

@api_router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str, current_user: User = Depends(get_current_user)):
    """Delete user prompt."""
    success = prompt_service.delete_user_prompt(prompt_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt non trouvé ou non autorisé")
    return {"message": "Prompt supprimé avec succès"}

@api_router.post("/prompts/{prompt_id}/duplicate", response_model=UserPrompt)
async def duplicate_prompt(
    prompt_id: str,
    new_title: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Duplicate a prompt."""
    duplicated = prompt_service.duplicate_prompt(prompt_id, current_user.id, new_title)
    if not duplicated:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    return duplicated

# ===============================
# LLM Integration Routes
# ===============================

@api_router.post("/llm/chat/internal")
async def chat_internal(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with internal LLM."""
    # Get prompt and fill with context
    prompt_data = prompt_service.get_prompt_by_id(request.prompt_id, current_user.id)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Fill prompt with variables
    filled_prompt = prompt_data['content']
    for var, value in request.context_variables.items():
        filled_prompt = filled_prompt.replace(f"{{{var}}}", value)
    
    # Create LLM request
    llm_request = LLMRequest(prompt=filled_prompt, stream=True)
    
    # Stream response
    async def generate():
        async for chunk in llm_service.chat_internal(llm_request):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@api_router.post("/llm/chat/ollama")
async def chat_ollama(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with Ollama."""
    # Get prompt and fill with context
    prompt_data = prompt_service.get_prompt_by_id(request.prompt_id, current_user.id)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Fill prompt with variables
    filled_prompt = prompt_data['content']
    for var, value in request.context_variables.items():
        filled_prompt = filled_prompt.replace(f"{{{var}}}", value)
    
    # Create LLM request
    llm_request = LLMRequest(prompt=filled_prompt, stream=True)
    
    # Stream response
    async def generate():
        async for chunk in llm_service.chat_ollama(llm_request):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@api_router.post("/llm/generate-external")
async def generate_external_prompt(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Generate prompt for external LLM use."""
    user_id = current_user.id if current_user else None
    
    # Get prompt and fill with context
    prompt_data = prompt_service.get_prompt_by_id(request.prompt_id, user_id)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Fill prompt with variables
    filled_prompt = prompt_data['content']
    for var, value in request.context_variables.items():
        filled_prompt = filled_prompt.replace(f"{{{var}}}", value)
    
    # Check privacy if enabled
    privacy_result = await llm_service.check_privacy(filled_prompt)
    
    return {
        "prompt": filled_prompt,
        "privacy_check": privacy_result,
        "external_links": {
            "chatgpt": "https://chat.openai.com/",
            "claude": "https://claude.ai/",
            "perplexity": "https://www.perplexity.ai/",
            "gemini": "https://gemini.google.com/"
        }
    }

@api_router.post("/llm/chat/server")
async def chat_with_specific_server(
    request: ChatRequest,
    server_name: str,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Chat with a specific LLM server."""
    # Get prompt and fill with context
    prompt_data = prompt_service.get_prompt_by_id(request.prompt_id, current_user.id)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Fill prompt with variables
    filled_prompt = prompt_data['content']
    for var, value in request.context_variables.items():
        filled_prompt = filled_prompt.replace(f"{{{var}}}", value)
    
    # Create LLM request
    llm_request = LLMRequest(prompt=filled_prompt, stream=True, model=model)
    
    # Stream response
    async def generate():
        async for chunk in llm_service.chat_with_server(server_name, llm_request, model):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@api_router.get("/llm/servers")
async def get_llm_servers():
    """Get all configured LLM servers."""
    servers = llm_service.get_servers()
    return {
        name: {
            "name": server.name,
            "type": server.type,
            "url": server.url,
            "default_model": server.default_model,
            "has_api_key": server.api_key is not None
        }
        for name, server in servers.items()
    }

@api_router.get("/llm/servers/{server_name}/test")
async def test_llm_server(server_name: str):
    """Test connectivity to a specific LLM server."""
    test_result = await llm_service.test_server(server_name)
    return test_result

@api_router.get("/llm/servers/test-all")
async def test_all_llm_servers():
    """Test connectivity to all configured LLM servers."""
    test_results = await llm_service.test_all_servers()
    return test_results

@api_router.get("/llm/servers/{server_name}/models")
async def get_server_models(server_name: str):
    """Get available models for a specific server."""
    models = await llm_service.get_server_models(server_name)
    return {"models": models}

@api_router.get("/llm/models")
async def get_available_models():
    """Get available LLM models.""" 
    models = llm_service.get_available_models()
    
    # Get dynamic models for servers that support it
    servers = llm_service.get_servers()
    for server_name, server in servers.items():
        try:
            dynamic_models = await llm_service.get_server_models(server_name)
            if dynamic_models:
                models[server_name] = dynamic_models
        except:
            pass  # Keep default model if dynamic fetch fails
    
    return models

# ===============================
# User Preferences Routes
# ===============================

@api_router.get("/user/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: User = Depends(get_current_user)):
    """Get current user preferences."""
    return UserPreferences(
        preferred_llm_server=current_user.preferred_llm_server,
        preferred_model=current_user.preferred_model
    )

@api_router.put("/user/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences."""
    updated_user = auth_service.update_user(
        current_user.uid,
        preferred_llm_server=preferences.preferred_llm_server,
        preferred_model=preferences.preferred_model
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"message": "Préférences mises à jour avec succès"}

# ===============================
# File Upload Routes
# ===============================

def _save_file_metadata(file_id: str, metadata: dict):
    """Save file metadata to JSON file."""
    metadata_file = FILES_DIR / f"{file_id}_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

def _load_file_metadata(file_id: str) -> Optional[dict]:
    """Load file metadata from JSON file."""
    metadata_file = FILES_DIR / f"{file_id}_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None

@api_router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and extract text from PDF file."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        extracted_text = ""
        
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        file_id = str(uuid.uuid4())
        
        # Store file in file system
        file_path = FILES_DIR / f"{file_id}.pdf"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Save metadata
        metadata = {
            "id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "extracted_text": extracted_text,
            "uploaded_by": current_user.id,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        _save_file_metadata(file_id, metadata)
        
        return {
            "id": file_id,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement du fichier")

@api_router.get("/files/{file_id}")
async def get_file_info(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get file information and metadata."""
    metadata = _load_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Check if user has access (own file or admin)
    if metadata["uploaded_by"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return metadata

@api_router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download the original PDF file."""
    metadata = _load_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Check if user has access
    if metadata["uploaded_by"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    file_path = FILES_DIR / f"{file_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier physique non trouvé")
    
    return {"download_url": f"/api/files/{file_id}/raw"}

@api_router.get("/files/{file_id}/raw")
async def get_raw_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get raw file content."""
    metadata = _load_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Check if user has access
    if metadata["uploaded_by"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    file_path = FILES_DIR / f"{file_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier physique non trouvé")
    
    def file_generator():
        with open(file_path, 'rb') as f:
            yield from f
    
    return StreamingResponse(
        file_generator(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={metadata['filename']}"}
    )

@api_router.get("/files")
async def list_user_files(current_user: User = Depends(get_current_user)):
    """List all files uploaded by the current user."""
    user_files = []
    
    # Scan files directory for user's files
    for metadata_file in FILES_DIR.glob("*_metadata.json"):
        metadata = _load_file_metadata(metadata_file.stem.replace("_metadata", ""))
        if metadata and metadata["uploaded_by"] == current_user.id:
            user_files.append({
                "id": metadata["id"],
                "filename": metadata["filename"],
                "size": metadata["size"],
                "uploaded_at": metadata["uploaded_at"]
            })
    
    return {"files": user_files}

@api_router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file."""
    metadata = _load_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Check if user has access
    if metadata["uploaded_by"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Delete files
    file_path = FILES_DIR / f"{file_id}.pdf"
    metadata_path = FILES_DIR / f"{file_id}_metadata.json"
    
    if file_path.exists():
        file_path.unlink()
    if metadata_path.exists():
        metadata_path.unlink()
    
    return {"message": "Fichier supprimé avec succès"}

# ===============================
# User Management Routes (Admin)
# ===============================

@api_router.get("/admin/users", response_model=List[User])
async def list_users(admin_user: User = Depends(get_admin_user)):
    """List all users (admin only)."""
    return auth_service.list_users()

@api_router.post("/admin/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(get_admin_user)
):
    """Create new user (admin only)."""
    try:
        return auth_service.create_user(
            user_data.uid,
            user_data.email,
            user_data.full_name,
            "default_password",  # User should change on first login
            user_data.role
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.put("/admin/users/{user_uid}", response_model=User)
async def update_user(
    user_uid: str,
    user_data: UserUpdate,
    admin_user: User = Depends(get_admin_user)
):
    """Update user (admin only)."""
    updated_user = auth_service.update_user(user_uid, **user_data.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return updated_user

@api_router.delete("/admin/users/{user_uid}")
async def delete_user(
    user_uid: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    success = auth_service.delete_user(user_uid)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

# ===============================
# Cockpit Variables Routes
# ===============================

@api_router.get("/cockpit/variables", response_model=List[CockpitVariable])
async def get_cockpit_variables():
    """Get all available Cockpit variables."""
    return cockpit_service.get_all_variables()

@api_router.get("/cockpit/variables/dict")
async def get_cockpit_variables_dict():
    """Get Cockpit variables as a dictionary."""
    return cockpit_service.get_variables_dict()

@api_router.post("/cockpit/extract-variables")
async def extract_cockpit_variables(content: Dict[str, str]):
    """Extract Cockpit variables from prompt content."""
    prompt_content = content.get("content", "")
    variables = cockpit_service.extract_cockpit_variables_from_content(prompt_content)
    uses_cockpit = cockpit_service.check_uses_cockpit_data(variables)
    
    return {
        "cockpit_variables": variables,
        "uses_cockpit_data": uses_cockpit,
        "formatted_variables": cockpit_service.format_variables_for_prompt(variables)
    }

# ===============================  
# User LLM Server Routes
# ===============================

@api_router.get("/user/llm-servers", response_model=List[UserLLMServer])
async def get_user_llm_servers(current_user: User = Depends(get_current_user)):
    """Get all LLM servers for the current user."""
    return user_llm_server_service.get_user_servers(current_user.id)

@api_router.get("/user/llm-servers/all")
async def get_all_available_servers(current_user: User = Depends(get_current_user)):
    """Get all available servers (system + user) for the current user."""
    return user_llm_server_service.get_all_available_servers(current_user.id)

@api_router.post("/user/llm-servers", response_model=UserLLMServer)
async def create_user_llm_server(
    server_data: UserLLMServerCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new LLM server for the user."""
    return user_llm_server_service.create_server(current_user.id, server_data)

@api_router.get("/user/llm-servers/{server_id}", response_model=UserLLMServer)
async def get_user_llm_server(
    server_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific user LLM server."""
    server = user_llm_server_service.get_server(server_id, current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return server

@api_router.put("/user/llm-servers/{server_id}", response_model=UserLLMServer)
async def update_user_llm_server(
    server_id: str,
    updates: UserLLMServerUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a user LLM server."""
    server = user_llm_server_service.update_server(server_id, current_user.id, updates)
    if not server:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return server

@api_router.delete("/user/llm-servers/{server_id}")
async def delete_user_llm_server(
    server_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a user LLM server."""
    success = user_llm_server_service.delete_server(server_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return {"message": "Serveur LLM supprimé avec succès"}

@api_router.post("/user/llm-servers/{server_id}/test")
async def test_user_llm_server(
    server_id: str,
    current_user: User = Depends(get_current_user)
):
    """Test connection to a user LLM server."""
    server = user_llm_server_service.get_server(server_id, current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    
    # Test asynchrone
    import aiohttp
    import time
    
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
                        
    except aiohttp.ClientError:
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

# ===============================
# Category Routes  
# ===============================

@api_router.get("/categories", response_model=List[Category])
async def get_categories(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Get all categories available to the user."""
    user_id = current_user.id if current_user else None
    return category_service.get_categories_by_user(user_id)

@api_router.get("/categories/dict")
async def get_categories_dict(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Get categories as a dictionary."""
    return category_service.get_categories_dict()

@api_router.post("/categories", response_model=Category)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new user category."""
    return category_service.create_category(category_data, current_user.id)

@api_router.put("/categories/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    updates: CategoryUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a user category."""
    category = category_service.update_category(category_id, updates, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée ou non autorisée")
    return category

@api_router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a user category."""
    success = category_service.delete_category(category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée ou non autorisée")
    return {"message": "Catégorie supprimée avec succès"}

@api_router.post("/categories/suggest")
async def suggest_category(data: Dict[str, str]):
    """Suggest a category for a prompt based on its content."""
    title = data.get("title", "")
    content = data.get("content", "")
    
    suggested_category_id = category_service.suggest_category_for_prompt(title, content)
    
    if suggested_category_id:
        category = category_service.get_category(suggested_category_id)
        return {
            "suggested_category_id": suggested_category_id,
            "suggested_category_name": category.name if category else None
        }
    
    return {"suggested_category_id": None, "suggested_category_name": None}

# ===============================
# Admin LLM Server Routes
# ===============================

@api_router.get("/admin/llm-servers")
async def get_admin_llm_servers(admin_user: User = Depends(get_admin_user)):
    """Get all system LLM servers (admin only)."""
    return admin_llm_server_service.get_all_servers()

@api_router.post("/admin/llm-servers")
async def create_admin_llm_server(
    server_data: AdminLLMServerCreate,
    admin_user: User = Depends(get_admin_user)
):
    """Create a new system LLM server (admin only)."""
    return admin_llm_server_service.create_server(server_data.dict())

@api_router.get("/admin/llm-servers/{server_id}")
async def get_admin_llm_server(
    server_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get a specific system LLM server (admin only)."""
    server = admin_llm_server_service.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return server

@api_router.put("/admin/llm-servers/{server_id}")
async def update_admin_llm_server(
    server_id: str,
    updates: AdminLLMServerUpdate,
    admin_user: User = Depends(get_admin_user)
):
    """Update a system LLM server (admin only)."""
    server = admin_llm_server_service.update_server(server_id, updates.dict(exclude_unset=True))
    if not server:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return server

@api_router.delete("/admin/llm-servers/{server_id}")
async def delete_admin_llm_server(
    server_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete a system LLM server (admin only)."""
    success = admin_llm_server_service.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Serveur LLM non trouvé")
    return {"message": "Serveur LLM supprimé avec succès"}

@api_router.post("/admin/llm-servers/{server_id}/test")
async def test_admin_llm_server(
    server_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Test connection to a system LLM server (admin only)."""
    result = admin_llm_server_service.test_server_connection(server_id)
    return result

# ===============================
# Enhanced Prompt Routes
# ===============================

@api_router.post("/prompts/import-new")
async def import_new_prompts(admin_user: User = Depends(get_admin_user)):
    """Import new prompts from the predefined collection (admin only)."""
    try:
        # Import the new prompts
        import sys
        sys.path.append(str(ROOT_DIR))
        from import_prompts import import_new_prompts
        
        result = import_new_prompts()
        
        # Reload prompt service to pick up new prompts
        prompt_service._load_system_prompts()
        
        return {
            "message": "Nouveaux prompts importés avec succès",
            "total_prompts": len(result.get("system_prompts", []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'import: {str(e)}")

# ===============================
# Prompt Execution Routes
# ===============================

@api_router.post("/prompts/{prompt_id}/validate")
async def validate_prompt_execution(
    prompt_id: str,
    variables: List[PromptVariable],
    current_user: User = Depends(get_current_user)
):
    """Validate prompt execution variables."""
    # Get prompt
    prompt = prompt_service.get_prompt_by_id(prompt_id, current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Validate variables
    validation = prompt_execution_service.validate_variables(prompt.content, variables)
    
    return validation

@api_router.post("/prompts/{prompt_id}/build-final")
async def build_final_prompt(
    prompt_id: str,
    request: PromptExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Build the final prompt with variables and files substituted."""
    # Get prompt
    prompt = prompt_service.get_prompt_by_id(prompt_id, current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Use modified content if provided, otherwise use original
    content = request.modified_content or prompt.content
    
    # Build final prompt
    final_prompt, logs = prompt_execution_service.build_final_prompt(
        content,
        request.variables,
        request.files
    )
    
    return {
        "original_content": prompt.content,
        "modified_content": request.modified_content,
        "final_prompt": final_prompt,
        "logs": logs
    }

@api_router.post("/prompts/{prompt_id}/execute")
async def execute_prompt(
    prompt_id: str,
    request: PromptExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute a prompt with full logging."""
    # Get prompt
    prompt = prompt_service.get_prompt(prompt_id, current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Use modified content if provided, otherwise use original
    content = request.modified_content or prompt.content
    
    # Validate variables first
    validation = prompt_execution_service.validate_variables(content, request.variables)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Variables manquantes: {', '.join(validation['missing_variables'])}"
        )
    
    # Get server configuration
    server_config = None
    
    if request.server_id:
        if request.server_id.startswith("system_"):
            # System server
            server_name = request.server_id[7:]  # Remove "system_" prefix
            server_config = admin_llm_server_service.get_server(server_name)
        else:
            # User server
            user_server = user_llm_server_service.get_server(request.server_id, current_user.id)
            if user_server:
                server_config = {
                    "type": user_server.type,
                    "url": user_server.url,
                    "api_key": user_server.api_key,
                    "default_model": user_server.default_model
                }
    
    if not server_config:
        # Use default system server
        servers = admin_llm_server_service.get_all_servers()
        if not servers:
            raise HTTPException(status_code=500, detail="Aucun serveur LLM disponible")
        server_config = servers[0]
    
    # Execute prompt
    result = await prompt_execution_service.execute_prompt(
        request,
        prompt.content,
        server_config
    )
    
    return result

@api_router.get("/prompts/executions/{execution_id}")
async def get_execution_result(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get execution result by ID."""
    result = prompt_execution_service.get_execution_result(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail="Résultat d'exécution non trouvé")
    
    return result

@api_router.get("/prompts/{prompt_id}/stream")
async def stream_prompt_execution(
    prompt_id: str,
    variables: str = "",  # JSON encoded variables
    modified_content: str = "",
    files: str = "",  # JSON encoded files
    server_id: str = "",
    model: str = "",
    current_user: User = Depends(get_current_user)
):
    """Stream prompt execution results."""
    from fastapi.responses import StreamingResponse
    import json
    
    # Get prompt
    prompt = prompt_service.get_prompt(prompt_id, current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    
    # Parse parameters
    try:
        variables_list = json.loads(variables) if variables else []
        files_list = json.loads(files) if files else []
        variables_obj = [PromptVariable(**var) for var in variables_list]
    except:
        variables_obj = []
        files_list = []
    
    # Use modified content if provided
    content = modified_content or prompt.content
    
    # Get server configuration
    server_config = None
    if server_id:
        if server_id.startswith("system_"):
            server_name = server_id[7:]
            server_config = admin_llm_server_service.get_server(server_name)
        else:
            user_server = user_llm_server_service.get_server(server_id, current_user.id)
            if user_server:
                server_config = {
                    "type": user_server.type,
                    "url": user_server.url,
                    "api_key": user_server.api_key,
                    "default_model": user_server.default_model
                }
    
    if not server_config:
        servers = admin_llm_server_service.get_all_servers()
        if servers:
            server_config = servers[0]
    
    if not server_config:
        raise HTTPException(status_code=500, detail="Aucun serveur LLM disponible")
    
    # Build final prompt
    final_prompt, _ = prompt_execution_service.build_final_prompt(
        content,
        variables_obj,
        files_list
    )
    
    # Determine model
    final_model = model or server_config.get('default_model', 'llama3')
    
    # Stream execution
    async def generate():
        async for chunk in prompt_execution_service.execute_prompt_streaming(
            final_prompt,
            server_config,
            final_model
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# ===============================
# Health Check Routes
# ===============================

@api_router.get("/")
async def root():
    """Health check endpoint."""
    app_config = get_app_config()
    return {
        "message": f"Bienvenue sur {app_config['title']}",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health")
async def health_check():
    """Detailed health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "llm": {}
        }
    }
    
    # Check LLM services
    models = llm_service.get_available_models()
    for service, model_list in models.items():
        health_status["services"]["llm"][service] = "available" if model_list else "unavailable"
    
    return health_status

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    pass
