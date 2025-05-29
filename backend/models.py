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
    content: str
    variables: List[str] = []
    accepts_files: bool = False
    needs_cockpit: bool = False
    category: str = "General"
    welcome_page_html: str = ""

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
    content: str
    variables: List[str] = []
    accepts_files: bool = False
    needs_cockpit: bool = False
    category: str = "General"
    welcome_page_html: str = ""
    type: PromptType
    is_public: bool = False
    based_on_system_prompt: Optional[str] = None

class UserPromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    accepts_files: Optional[bool] = None
    needs_cockpit: Optional[bool] = None
    category: Optional[str] = None
    welcome_page_html: Optional[str] = None
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
