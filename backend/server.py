from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import PyPDF2
import io

from models import (
    User, UserLogin, Token, UserCreate, UserUpdate,
    UserPrompt, UserPromptCreate, UserPromptUpdate,
    ChatRequest, LLMRequest, PromptExecutionResult,
    LLMServerConfig, LLMServerTest, UserPreferences
)
from services import AuthService, PromptService, LLMService
from config import get_app_config, get_database_config

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db_config = get_database_config()
db = client[os.environ.get('DB_NAME', db_config['prompts_db_name'])]

# Initialize services
auth_service = AuthService()
prompt_service = PromptService()
llm_service = LLMService()

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
        from models import PromptType
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
        
        # Store in MongoDB (optional - for now just return the text)
        file_doc = {
            "id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "extracted_text": extracted_text,
            "uploaded_by": current_user.id,
            "uploaded_at": datetime.utcnow()
        }
        
        await db.files.insert_one(file_doc)
        
        return {
            "id": file_id,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement du fichier")

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
    client.close()
