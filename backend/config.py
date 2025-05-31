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
        possible_paths = [
            os.environ.get('PROMPTACHAT_CONFIG'),
            '/app/config.ini',
            '/app/config.ini.template',
            './config.ini',
            './config.ini.template'
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return path
                
        # Create default config if none found
        default_path = '/app/config.ini'
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path: str):
        """Create default configuration file."""
        logger.warning(f"No config file found, creating default at {path}")
        template_path = '/app/config.ini.template'
        if Path(template_path).exists():
            import shutil
            shutil.copy(template_path, path)
        else:
            # Create minimal config
            with open(path, 'w') as f:
                f.write("""[app]
name = edf
title = PromptAchat

[database]
prompts_db_name = promptachat_db

[ollama]
enabled = true
url = http://localhost:11434/v1
default_model = llama3

[logging]
default_level = INFO
""")
    
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
