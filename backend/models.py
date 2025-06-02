from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums
class PromptType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ConfidentialityLevel(str, Enum):
    C0 = "C0"  # Public
    C1 = "C1"  # Interne
    C2 = "C2"  # Confidentiel
    C3 = "C3"  # Secret

# Prompt Models
class PromptBase(BaseModel):
    title: str
    description: Optional[str] = ""
    content: str
    variables: List[str] = []
    accepts_files: bool = False
    uses_cockpit_data: bool = False  # Changed from needs_cockpit
    category: str = "General"
    welcome_page_html: str = ""
    is_system: bool = False  # Added for system prompts

class SystemPrompt(PromptBase):
    id: str
    type: PromptType

class UserPrompt(PromptBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: PromptType
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    based_on_system_prompt: Optional[str] = None

class UserPromptCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    content: str
    variables: List[str] = []
    accepts_files: bool = False
    uses_cockpit_data: bool = False  # Changed from needs_cockpit
    category: str = "General"
    welcome_page_html: str = ""
    type: PromptType
    is_public: bool = False
    based_on_system_prompt: Optional[str] = None

class UserPromptUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    accepts_files: Optional[bool] = None
    uses_cockpit_data: Optional[bool] = None  # Changed from needs_cockpit
    category: Optional[str] = None
    welcome_page_html: Optional[str] = None
    type: Optional[PromptType] = None
    is_public: Optional[bool] = None

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uid: str  # LDAP UID or local username
    email: str
    full_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    auth_source: str = "local"  # "ldap" or "local"
    preferred_llm_server: Optional[str] = None  # Serveur LLM préféré
    preferred_model: Optional[str] = None  # Modèle préféré

class UserCreate(BaseModel):
    uid: str
    email: str
    full_name: str
    role: UserRole = UserRole.USER
    auth_source: str = "local"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# Authentication Models
class UserLogin(BaseModel):
    uid: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    uid: Optional[str] = None

# Chat Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    prompt_id: str
    messages: List[ChatMessage] = []
    context_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    prompt_id: str
    user_message: str
    context_variables: Dict[str, str] = {}
    cockpit_id: Optional[str] = None
    session_id: Optional[str] = None

# LLM Models
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = True

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int] = {}
    confidentiality_level: Optional[ConfidentialityLevel] = None

# File Models
class FileUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content_type: str
    size: int
    extracted_text: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

# Cockpit Models
class CockpitData(BaseModel):
    id: str
    data: Dict[str, Any]
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

# Response Models
class PromptExecutionResult(BaseModel):
    prompt_id: str
    filled_prompt: str
    context_used: Dict[str, Any]
    execution_type: PromptType
    confidentiality_level: Optional[ConfidentialityLevel] = None
    session_id: Optional[str] = None

class PrivacyCheckResult(BaseModel):
    text: str
    confidentiality_level: ConfidentialityLevel
    concerns: List[str] = []
    recommendations: List[str] = []

# LLM Server Models
class LLMServerConfig(BaseModel):
    name: str
    type: str  # "ollama" or "openai"
    url: str
    api_key: Optional[str] = None
    default_model: str
    is_available: bool = False

class LLMServerTest(BaseModel):
    server_name: str
    status: str  # "success", "error", "timeout"
    message: str
    response_time: Optional[float] = None
    available_models: List[str] = []

class UserPreferences(BaseModel):
    preferred_llm_server: Optional[str] = None
    preferred_model: Optional[str] = None

# User LLM Server Models (pour la gestion utilisateur)
class UserLLMServer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    type: str  # "ollama" or "openai" 
    url: str
    api_key: Optional[str] = None
    default_model: str
    port: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserLLMServerCreate(BaseModel):
    name: str
    type: str  # "ollama" or "openai"
    url: str
    api_key: Optional[str] = None
    default_model: str
    port: Optional[int] = None

class UserLLMServerUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    port: Optional[int] = None
    is_active: Optional[bool] = None

# Cockpit Variables Models
class CockpitVariable(BaseModel):
    key: str
    label: str
    description: Optional[str] = None

# Admin LLM Server Models (pour la gestion par les administrateurs)
class AdminLLMServerCreate(BaseModel):
    name: str
    type: str  # "ollama" or "openai"
    url: str
    api_key: Optional[str] = None
    default_model: str

class AdminLLMServerUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None

# Prompt Execution Models
class PromptVariable(BaseModel):
    name: str
    value: str
    is_cockpit: bool = False

class PromptExecutionRequest(BaseModel):
    prompt_id: str
    variables: List[PromptVariable] = []
    modified_content: Optional[str] = None
    files: List[str] = []  # Base64 encoded files
    server_id: Optional[str] = None
    model: Optional[str] = None

class PromptExecutionLog(BaseModel):
    timestamp: datetime
    action: str  # "variable_substitution", "file_processing", "api_call", "response"
    details: str
    success: bool = True

class PromptExecutionResult(BaseModel):
    execution_id: str
    prompt_id: str
    final_prompt: str
    result: str
    logs: List[PromptExecutionLog]
    execution_time: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

# Category Models
class Category(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_system: bool = False

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
