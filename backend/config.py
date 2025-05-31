import configparser
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for PromptAchat application."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = configparser.ConfigParser()
        self.config_file = config_file or self._find_config_file()
        self._load_config()
        
    def _find_config_file(self) -> str:
        """Find configuration file in order of preference."""
        # Get the current directory (backend) and parent directory (project root)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        possible_paths = [
            os.environ.get('PROMPTACHAT_CONFIG'),
            # Docker environment paths (for backward compatibility)
            '/app/config.ini',
            # Local development paths (Windows/Linux compatible)
            str(project_root / 'config.ini'),
            str(current_dir / 'config.ini'),
            str(project_root / 'config.ini.template'),
            str(current_dir / 'config.ini.template'),
            # Fallback relative paths
            '../config.ini',
            './config.ini',
            '../config.ini.template',
            './config.ini.template'
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                logger.info(f"Found config file at: {path}")
                return str(Path(path).resolve())
                
        # Create default config if none found
        # Try project root first, then current directory
        default_path = project_root / 'config.ini'
        template_path = project_root / 'config.ini.template'
        
        # If we can't write to project root, use current directory
        try:
            default_path.parent.mkdir(parents=True, exist_ok=True)
            default_path.touch()
            default_path.unlink()  # Just testing write permission
        except (PermissionError, OSError):
            default_path = current_dir / 'config.ini'
            template_path = current_dir / 'config.ini.template'
        
        self._create_default_config(str(default_path), str(template_path))
        return str(default_path)
    
    def _create_default_config(self, path: str, template_path: str = None):
        """Create default configuration file."""
        logger.warning(f"No config file found, creating default at {path}")
        
        # Try to copy from template first
        if template_path and Path(template_path).exists():
            try:
                import shutil
                shutil.copy(template_path, path)
                logger.info(f"Copied template from {template_path} to {path}")
                return
            except Exception as e:
                logger.warning(f"Could not copy template: {e}")
        
        # Create minimal config if template not available
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("""[app]
name = edf
title = PromptAchat - Bibliothèque de Prompts EDF
logo_url = https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/EDF_logo.svg/1200px-EDF_logo.svg.png
access_contact_email = contact@edf.fr
session_timeout = 3600

[database]
user_auth_db_path = user_auth.db
prompts_db_name = promptachat_db

[file_storage]
storage_type = filesystem
base_directory = uploaded_files
max_file_size_mb = 10
allowed_extensions = pdf
cleanup_temp_files = true
keep_file_days = 365

[llm_servers]
# Format: server_name = type|url|api_key|default_model
# Types supportés: ollama, openai
server1 = ollama|http://localhost:11434|none|llama3

[ollama]
enabled = false
url = http://localhost:11434/v1
default_model = llama3

[llm]
default_temperature = 0.7
max_tokens = 4096
timeout = 120

[ldap]
enabled = false
server = ldap.example.com
port = 389
user_dn_format = uid=%%s,ou=people,dc=example,dc=com
use_ssl = false
base_dn = dc=example,dc=com

[security]
initial_admin_uids = admin,admin1,admin2
jwt_secret_key = CHANGEZ_MOI_EN_PRODUCTION
jwt_algorithm = HS256
jwt_expire_minutes = 60

[logging]
default_level = INFO
max_log_size = 10MB
backup_count = 5

[features]
enable_privacy_check = true
enable_deep_linking = true
enable_pdf_upload = true
enable_cockpit_integration = true
max_file_size_mb = 10
""")
            logger.info(f"Created minimal config at {path}")
        except Exception as e:
            logger.error(f"Could not create config file: {e}")
            raise
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            self.config.read(self.config_file)
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value with environment variable override."""
        # Check environment variable first
        env_key = f"PROMPTACHAT_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
            
        # Then check config file
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value."""
        env_key = f"PROMPTACHAT_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value.lower() in ('true', '1', 'yes', 'on')
            
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value."""
        env_key = f"PROMPTACHAT_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            try:
                return int(env_value)
            except ValueError:
                return fallback
                
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value."""
        env_key = f"PROMPTACHAT_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            try:
                return float(env_value)
            except ValueError:
                return fallback
                
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire section as dictionary."""
        if not self.config.has_section(section):
            return {}
        return dict(self.config.items(section))
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()

# Global configuration instance
config = Config()

# Helper functions for common configurations
def get_database_config():
    """Get database configuration."""
    return {
        'prompts_db_name': config.get('database', 'prompts_db_name', 'promptachat_db'),
        'user_auth_db_path': config.get('database', 'user_auth_db_path', 'user_auth.db')
    }

def get_llm_config():
    """Get LLM configuration."""
    return {
        'internal': {
            'url': config.get('internal', 'url', 'http://localhost:8080/v1'),
            'api_key': config.get('internal', 'api_key'),
            'default_model': config.get('internal', 'default_model', 'llama3')
        },
        'ollama': {
            'enabled': config.getboolean('ollama', 'enabled', True),
            'url': config.get('ollama', 'url', 'http://localhost:11434/v1'),
            'default_model': config.get('ollama', 'default_model', 'llama3')
        },
        'external': {
            'url': config.get('external', 'url'),
            'api_key': config.get('external', 'api_key'),
            'default_model': config.get('external', 'default_model', 'gpt-3.5-turbo')
        },
        'oneapi': {
            'use_oneapi': config.getboolean('oneapi', 'use_oneapi', False),
            'url': config.get('oneapi', 'oneapi_url'),
            'api_key': config.get('oneapi', 'api_key')
        },
        'default_temperature': config.getfloat('llm', 'default_temperature', 0.7),
        'max_tokens': config.getint('llm', 'max_tokens', 4096),
        'timeout': config.getint('llm', 'timeout', 120)
    }

def get_app_config():
    """Get application configuration."""
    return {
        'name': config.get('app', 'name', 'edf'),
        'title': config.get('app', 'title', 'PromptAchat'),
        'logo_url': config.get('app', 'logo_url'),
        'contact_email': config.get('app', 'access_contact_email', 'contact@example.com'),
        'session_timeout': config.getint('app', 'session_timeout', 3600)
    }

def get_auth_config():
    """Get authentication configuration."""
    return {
        'ldap': {
            'enabled': config.getboolean('ldap', 'enabled', False),
            'server': config.get('ldap', 'server'),
            'port': config.getint('ldap', 'port', 389),
            'user_dn_format': config.get('ldap', 'user_dn_format'),
            'use_ssl': config.getboolean('ldap', 'use_ssl', False),
            'base_dn': config.get('ldap', 'base_dn'),
            'bind_user': config.get('ldap', 'bind_user'),
            'bind_password': config.get('ldap', 'bind_password')
        },
        'jwt': {
            'secret_key': config.get('security', 'jwt_secret_key', 'CHANGEZ_MOI_EN_PRODUCTION'),
            'algorithm': config.get('security', 'jwt_algorithm', 'HS256'),
            'expire_minutes': config.getint('security', 'jwt_expire_minutes', 60)
        },
        'initial_admin_uids': config.get('security', 'initial_admin_uids', 'admin').split(',')
    }

def get_features_config():
    """Get features configuration."""
    return {
        'enable_privacy_check': config.getboolean('features', 'enable_privacy_check', True),
        'enable_deep_linking': config.getboolean('features', 'enable_deep_linking', True),
        'enable_pdf_upload': config.getboolean('features', 'enable_pdf_upload', True),
        'enable_cockpit_integration': config.getboolean('features', 'enable_cockpit_integration', True),
        'max_file_size_mb': config.getint('features', 'max_file_size_mb', 10)
    }

def get_cockpit_config():
    """Get Cockpit API configuration."""
    return {
        'api_url': config.get('cockpit', 'api_url'),
        'api_key': config.get('cockpit', 'api_key'),
        'verify_cert_path': config.get('cockpit', 'verify_cert_path'),
        'timeout': config.getint('cockpit', 'timeout', 30)
    }
