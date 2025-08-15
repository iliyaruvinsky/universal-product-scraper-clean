"""
Database operations for authentication system.

Handles SQLite database creation, user management, and data persistence.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path


class AuthDatabase:
    """Manages SQLite database operations for user authentication."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            # Default to data/auth/users.db
            project_root = Path(__file__).parent.parent.parent
            db_dir = project_root / "data" / "auth"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "users.db"
        
        self.db_path = str(db_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    password_expires_at TIMESTAMP NOT NULL,
                    must_change_password BOOLEAN DEFAULT 0,
                    last_login TIMESTAMP,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            """)
            
            conn.commit()
    
    def create_user(self, username: str, password_hash: str, 
                   must_change_password: bool = False) -> bool:
        """Create a new user."""
        try:
            # Password expires in 6 months
            password_expires = datetime.now() + timedelta(days=180)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users (username, password_hash, password_expires_at, must_change_password)
                    VALUES (?, ?, ?, ?)
                """, (username, password_hash, password_expires, must_change_password))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # User already exists
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_password(self, username: str, new_password_hash: str) -> bool:
        """Update user password."""
        try:
            password_expires = datetime.now() + timedelta(days=180)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE users 
                    SET password_hash = ?, password_expires_at = ?, must_change_password = 0
                    WHERE username = ?
                """, (new_password_hash, password_expires, username))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def update_last_login(self, username: str):
        """Update last login timestamp."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            """, (username,))
            conn.commit()
    
    def increment_failed_attempts(self, username: str) -> int:
        """Increment failed login attempts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET failed_attempts = failed_attempts + 1
                WHERE username = ?
            """, (username,))
            
            cursor = conn.execute("""
                SELECT failed_attempts FROM users WHERE username = ?
            """, (username,))
            result = cursor.fetchone()
            conn.commit()
            
            return result[0] if result else 0
    
    def reset_failed_attempts(self, username: str):
        """Reset failed login attempts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET failed_attempts = 0, locked_until = NULL
                WHERE username = ?
            """, (username,))
            conn.commit()
    
    def lock_user(self, username: str, lock_duration_minutes: int = 15):
        """Lock user account for specified duration."""
        locked_until = datetime.now() + timedelta(minutes=lock_duration_minutes)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET locked_until = ?
                WHERE username = ?
            """, (locked_until, username))
            conn.commit()
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete sessions first
                conn.execute("DELETE FROM sessions WHERE username = ?", (username,))
                # Delete user
                cursor = conn.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users with their info."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT username, created_at, password_expires_at, last_login, 
                       must_change_password, failed_attempts, locked_until
                FROM users 
                ORDER BY username
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def create_session(self, username: str, session_token: str, 
                      duration_hours: int = 8) -> bool:
        """Create a new session."""
        try:
            expires_at = datetime.now() + timedelta(hours=duration_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sessions (username, session_token, expires_at)
                    VALUES (?, ?, ?)
                """, (username, session_token, expires_at))
                conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """Validate session and return username if valid."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT username FROM sessions 
                WHERE session_token = ? AND expires_at > CURRENT_TIMESTAMP
            """, (session_token,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def delete_session(self, session_token: str):
        """Delete a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
            conn.commit()
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]