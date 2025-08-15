"""
Session management for authentication system.

Handles user sessions, tokens, and session persistence during CLI runtime.
"""

import secrets
import json
import tempfile
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from .database import AuthDatabase


class SessionManager:
    """Manages user sessions and authentication tokens."""
    
    def __init__(self, db: Optional[AuthDatabase] = None):
        """Initialize session manager."""
        self.db = db or AuthDatabase()
        self._current_session = None
        self._session_file = None
        
        # Clean up expired sessions on startup
        self.db.cleanup_expired_sessions()
    
    def create_session(self, username: str, duration_hours: int = 8) -> str:
        """
        Create a new session for the user.
        
        Args:
            username: Username to create session for
            duration_hours: Session duration in hours
            
        Returns:
            Session token
        """
        # Generate secure random token
        session_token = secrets.token_urlsafe(32)
        
        # Store in database
        success = self.db.create_session(username, session_token, duration_hours)
        
        if success:
            # Store current session info
            self._current_session = {
                'username': username,
                'token': session_token,
                'expires_at': (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # Create temporary session file for this CLI run
            self._create_session_file()
            
            return session_token
        else:
            raise RuntimeError("Failed to create session")
    
    def validate_session(self, session_token: Optional[str] = None) -> Optional[str]:
        """
        Validate a session token.
        
        Args:
            session_token: Token to validate (uses current if None)
            
        Returns:
            Username if valid, None if invalid
        """
        # Use current session token if none provided
        if session_token is None:
            session_token = self.get_current_token()
        
        if not session_token:
            return None
        
        # Check database
        username = self.db.validate_session(session_token)
        
        # Update current session if valid
        if username and self._current_session and self._current_session['token'] == session_token:
            self._current_session['last_accessed'] = datetime.now().isoformat()
        
        return username
    
    def get_current_user(self) -> Optional[str]:
        """Get currently authenticated user."""
        if self._current_session:
            username = self.validate_session()
            return username
        return None
    
    def get_current_token(self) -> Optional[str]:
        """Get current session token."""
        if self._current_session:
            return self._current_session['token']
        return None
    
    def is_authenticated(self) -> bool:
        """Check if there's a valid current session."""
        return self.get_current_user() is not None
    
    def logout(self):
        """Logout current user and invalidate session."""
        if self._current_session:
            # Remove from database
            self.db.delete_session(self._current_session['token'])
            
            # Clear current session
            self._current_session = None
            
            # Remove session file
            self._remove_session_file()
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information."""
        if not self._current_session:
            return None
        
        username = self.validate_session()
        if not username:
            return None
        
        expires_at = datetime.fromisoformat(self._current_session['expires_at'])
        time_left = expires_at - datetime.now()
        
        return {
            'username': username,
            'created_at': self._current_session['created_at'],
            'expires_at': self._current_session['expires_at'],
            'time_left_minutes': int(time_left.total_seconds() / 60),
            'time_left_hours': round(time_left.total_seconds() / 3600, 1)
        }
    
    def extend_session(self, additional_hours: int = 4) -> bool:
        """
        Extend current session by additional hours.
        
        Args:
            additional_hours: Hours to add to session
            
        Returns:
            True if extended successfully
        """
        if not self._current_session:
            return False
        
        username = self.validate_session()
        if not username:
            return False
        
        # Create new session with extended time
        try:
            # Delete current session
            self.db.delete_session(self._current_session['token'])
            
            # Create new extended session
            current_expires = datetime.fromisoformat(self._current_session['expires_at'])
            time_left = current_expires - datetime.now()
            total_hours = int(time_left.total_seconds() / 3600) + additional_hours
            
            new_token = self.create_session(username, total_hours)
            return True
            
        except Exception:
            return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database."""
        self.db.cleanup_expired_sessions()
    
    def _create_session_file(self):
        """Create temporary session file for CLI run."""
        if self._current_session:
            try:
                # Create temp file
                temp_dir = tempfile.gettempdir()
                session_file = os.path.join(temp_dir, f"ups_session_{os.getpid()}.json")
                
                with open(session_file, 'w') as f:
                    json.dump(self._current_session, f)
                
                self._session_file = session_file
                
            except Exception:
                # If we can't create session file, continue without it
                pass
    
    def _remove_session_file(self):
        """Remove temporary session file."""
        if self._session_file and os.path.exists(self._session_file):
            try:
                os.remove(self._session_file)
            except Exception:
                pass
            finally:
                self._session_file = None
    
    def restore_session_from_file(self) -> bool:
        """
        Attempt to restore session from temporary file.
        Used for debugging/development only.
        
        Returns:
            True if session restored
        """
        try:
            # Look for session files in temp directory
            temp_dir = tempfile.gettempdir()
            session_pattern = f"ups_session_{os.getpid()}.json"
            session_file = os.path.join(temp_dir, session_pattern)
            
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Validate the session is still valid
                username = self.db.validate_session(session_data['token'])
                if username:
                    self._current_session = session_data
                    self._session_file = session_file
                    return True
                else:
                    # Session expired, remove file
                    os.remove(session_file)
            
            return False
            
        except Exception:
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for monitoring."""
        with self.db._get_connection() if hasattr(self.db, '_get_connection') else self.db.db_path as conn:
            # This is a simplified version - you might want to add more stats
            return {
                'current_user': self.get_current_user(),
                'is_authenticated': self.is_authenticated(),
                'session_info': self.get_session_info()
            }
    
    def __del__(self):
        """Cleanup on destruction."""
        self._remove_session_file()