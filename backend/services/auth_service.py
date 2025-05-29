import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import logging
from pathlib import Path

try:
    import ldap3
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False
    logging.warning("LDAP3 not available. LDAP authentication disabled.")

from ..config import get_auth_config, get_database_config
from ..models import User, UserRole

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication (LDAP + local SQLite)."""
    
    def __init__(self):
        self.auth_config = get_auth_config()
        self.db_config = get_database_config()
        self.db_path = self.db_config['user_auth_db_path']
        self._init_local_db()
        
    def _init_local_db(self):
        """Initialize local SQLite database for user management."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    uid TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    password_hash TEXT,
                    salt TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    auth_source TEXT DEFAULT 'local',
                    preferred_llm_server TEXT,
                    preferred_model TEXT
                )
            ''')
            
            # Create initial admin users
            for admin_uid in self.auth_config['initial_admin_uids']:
                admin_uid = admin_uid.strip()
                if admin_uid:
                    self._create_initial_admin(conn, admin_uid)
            
            conn.commit()
    
    def _create_initial_admin(self, conn: sqlite3.Connection, uid: str):
        """Create initial admin user if not exists."""
        cursor = conn.execute('SELECT uid FROM users WHERE uid = ?', (uid,))
        if not cursor.fetchone():
            user_id = secrets.token_urlsafe(16)
            salt = secrets.token_hex(32)
            # Default password is same as UID for initial setup
            password_hash = self._hash_password(uid, salt)
            
            conn.execute('''
                INSERT INTO users (id, uid, email, full_name, role, password_hash, salt, auth_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, uid, f"{uid}@example.com", f"Admin {uid}",
                UserRole.ADMIN, password_hash, salt, "local"
            ))
            logger.info(f"Created initial admin user: {uid}")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt."""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def authenticate_ldap(self, uid: str, password: str) -> Optional[User]:
        """Authenticate user against LDAP."""
        if not LDAP_AVAILABLE or not self.auth_config['ldap']['enabled']:
            return None
            
        try:
            ldap_config = self.auth_config['ldap']
            server = ldap3.Server(
                ldap_config['server'],
                port=ldap_config['port'],
                use_ssl=ldap_config['use_ssl']
            )
            
            user_dn = ldap_config['user_dn_format'] % uid
            
            conn = ldap3.Connection(server, user=user_dn, password=password)
            if not conn.bind():
                return None
                
            # Get user attributes
            conn.search(
                ldap_config['base_dn'],
                f'(uid={uid})',
                attributes=['mail', 'cn', 'displayName']
            )
            
            if not conn.entries:
                return None
                
            entry = conn.entries[0]
            email = str(entry.mail) if hasattr(entry, 'mail') else f"{uid}@company.com"
            full_name = str(entry.cn) if hasattr(entry, 'cn') else uid
            
            # Store/update user in local DB
            user = self._store_ldap_user(uid, email, full_name)
            conn.unbind()
            
            return user
            
        except Exception as e:
            logger.error(f"LDAP authentication error: {e}")
            return None
    
    def authenticate_local(self, uid: str, password: str) -> Optional[User]:
        """Authenticate user against local SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM users WHERE uid = ? AND is_active = 1',
                (uid,)
            )
            user_row = cursor.fetchone()
            
            if not user_row:
                return None
                
            # Check password
            password_hash = self._hash_password(password, user_row['salt'])
            if password_hash != user_row['password_hash']:
                return None
                
            # Update last login
            conn.execute(
                'UPDATE users SET last_login = ? WHERE uid = ?',
                (datetime.utcnow(), uid)
            )
            
            return User(
                id=user_row['id'],
                uid=user_row['uid'],
                email=user_row['email'],
                full_name=user_row['full_name'],
                role=UserRole(user_row['role']),
                is_active=bool(user_row['is_active']),
                auth_source=user_row['auth_source'],
                preferred_llm_server=user_row['preferred_llm_server'],
                preferred_model=user_row['preferred_model'],
                last_login=datetime.fromisoformat(user_row['last_login']) if user_row['last_login'] else None
            )
    
    def authenticate(self, uid: str, password: str) -> Optional[User]:
        """Main authentication method - tries LDAP first, then local."""
        # Try LDAP first if enabled
        if self.auth_config['ldap']['enabled']:
            user = self.authenticate_ldap(uid, password)
            if user:
                return user
        
        # Fallback to local authentication
        return self.authenticate_local(uid, password)
    
    def _store_ldap_user(self, uid: str, email: str, full_name: str) -> User:
        """Store or update LDAP user in local database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Check if user exists
            cursor = conn.execute('SELECT * FROM users WHERE uid = ?', (uid,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                conn.execute('''
                    UPDATE users SET email = ?, full_name = ?, last_login = ?
                    WHERE uid = ?
                ''', (email, full_name, datetime.utcnow(), uid))
                
                return User(
                    id=existing_user['id'],
                    uid=uid,
                    email=email,
                    full_name=full_name,
                    role=UserRole(existing_user['role']),
                    is_active=bool(existing_user['is_active']),
                    auth_source="ldap",
                    preferred_llm_server=existing_user['preferred_llm_server'],
                    preferred_model=existing_user['preferred_model']
                )
            else:
                # Create new user
                user_id = secrets.token_urlsafe(16)
                conn.execute('''
                    INSERT INTO users (id, uid, email, full_name, role, is_active, auth_source, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, uid, email, full_name, UserRole.USER,
                    True, "ldap", datetime.utcnow()
                ))
                
                return User(
                    id=user_id,
                    uid=uid,
                    email=email,
                    full_name=full_name,
                    role=UserRole.USER,
                    is_active=True,
                    auth_source="ldap"
                )
    
    def create_user(self, uid: str, email: str, full_name: str, 
                   password: str, role: UserRole = UserRole.USER) -> User:
        """Create new local user."""
        with sqlite3.connect(self.db_path) as conn:
            user_id = secrets.token_urlsafe(16)
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            conn.execute('''
                INSERT INTO users (id, uid, email, full_name, role, password_hash, salt, auth_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, uid, email, full_name, role, password_hash, salt, "local"
            ))
            
            return User(
                id=user_id,
                uid=uid,
                email=email,
                full_name=full_name,
                role=role,
                is_active=True,
                auth_source="local"
            )
    
    def get_user_by_uid(self, uid: str) -> Optional[User]:
        """Get user by UID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM users WHERE uid = ?', (uid,))
            user_row = cursor.fetchone()
            
            if not user_row:
                return None
                
            return User(
                id=user_row['id'],
                uid=user_row['uid'],
                email=user_row['email'],
                full_name=user_row['full_name'],
                role=UserRole(user_row['role']),
                is_active=bool(user_row['is_active']),
                auth_source=user_row['auth_source'],
                preferred_llm_server=user_row['preferred_llm_server'],
                preferred_model=user_row['preferred_model']
            )
    
    def list_users(self) -> list[User]:
        """List all users."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM users ORDER BY full_name')
            
            users = []
            for row in cursor.fetchall():
                users.append(User(
                    id=row['id'],
                    uid=row['uid'],
                    email=row['email'],
                    full_name=row['full_name'],
                    role=UserRole(row['role']),
                    is_active=bool(row['is_active']),
                    auth_source=row['auth_source'],
                    preferred_llm_server=row['preferred_llm_server'],
                    preferred_model=row['preferred_model']
                ))
            
            return users
    
    def update_user(self, uid: str, **updates) -> Optional[User]:
        """Update user information."""
        with sqlite3.connect(self.db_path) as conn:
            # Build dynamic update query
            fields = []
            values = []
            
            for field, value in updates.items():
                if field in ['email', 'full_name', 'role', 'is_active', 'preferred_llm_server', 'preferred_model']:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if not fields:
                return self.get_user_by_uid(uid)
            
            values.append(uid)
            query = f"UPDATE users SET {', '.join(fields)} WHERE uid = ?"
            conn.execute(query, values)
            
            return self.get_user_by_uid(uid)
    
    def delete_user(self, uid: str) -> bool:
        """Delete user (mark as inactive)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'UPDATE users SET is_active = 0 WHERE uid = ?',
                (uid,)
            )
            return cursor.rowcount > 0
    
    def create_token(self, user: User) -> str:
        """Create JWT token for user."""
        payload = {
            'uid': user.uid,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(minutes=self.auth_config['jwt']['expire_minutes'])
        }
        
        return jwt.encode(
            payload,
            self.auth_config['jwt']['secret_key'],
            algorithm=self.auth_config['jwt']['algorithm']
        )
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.auth_config['jwt']['secret_key'],
                algorithms=[self.auth_config['jwt']['algorithm']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
