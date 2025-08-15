"""
Main authentication manager for Universal Product Scraper.

Provides high-level authentication operations, user management, and system initialization.
"""

import getpass
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from .database import AuthDatabase
from .password_utils import PasswordValidator, PasswordHasher, PasswordStrengthMeter
from .session_manager import SessionManager


class AuthManager:
    """Main authentication manager handling all auth operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize authentication manager."""
        self.db = AuthDatabase(db_path)
        self.session_manager = SessionManager(self.db)
        self.password_validator = PasswordValidator()
        self.password_hasher = PasswordHasher()
        
        # Initialize default admin user if no users exist
        self._initialize_default_admin()
    
    def _initialize_default_admin(self):
        """Create default admin user if no users exist."""
        if self.db.get_user_count() == 0:
            # Create default admin with temporary password
            default_password = "Admin@123"
            password_hash = self.password_hasher.hash_password(default_password)
            
            success = self.db.create_user(
                username="admin",
                password_hash=password_hash,
                must_change_password=True
            )
            
            if success:
                print("ℹ️  Default admin user created:")
                print("   Username: admin")
                print("   Password: Admin@123")
                print("   ⚠️  You MUST change this password on first login!")
                print()
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, bool]:
        """
        Authenticate a user.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Tuple of (success, message, must_change_password)
        """
        user = self.db.get_user(username)
        if not user:
            return False, "Invalid username or password", False
        
        # Check if account is locked
        if user['locked_until']:
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.now() < locked_until:
                minutes_left = int((locked_until - datetime.now()).total_seconds() / 60)
                return False, f"Account locked. Try again in {minutes_left} minutes", False
        
        # Check password
        if not self.password_hasher.verify_password(password, user['password_hash']):
            failed_attempts = self.db.increment_failed_attempts(username)
            
            if failed_attempts >= 5:
                self.db.lock_user(username, 15)  # Lock for 15 minutes
                return False, "Too many failed attempts. Account locked for 15 minutes", False
            else:
                remaining = 5 - failed_attempts
                return False, f"Invalid password. {remaining} attempts remaining", False
        
        # Check password expiry
        password_expires = datetime.fromisoformat(user['password_expires_at'])
        if datetime.now() > password_expires:
            return False, "Password has expired. Please contact administrator", True
        
        # Authentication successful
        self.db.reset_failed_attempts(username)
        self.db.update_last_login(username)
        
        # Create session
        session_token = self.session_manager.create_session(username)
        
        return True, "Authentication successful", user['must_change_password']
    
    def login_flow(self) -> bool:
        """
        Handle complete login flow with user interaction.
        
        Returns:
            True if login successful
        """
        print("🔐 Universal Product Scraper - Authentication Required")
        print("=" * 50)
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                # Get credentials
                username = input("Username: ").strip()
                if not username:
                    print("❌ Username cannot be empty")
                    continue
                
                password = getpass.getpass("Password: ")
                if not password:
                    print("❌ Password cannot be empty")
                    continue
                
                # Authenticate
                success, message, must_change = self.authenticate_user(username, password)
                
                if success:
                    print(f"✅ {message}")
                    
                    # Handle password change requirement
                    if must_change:
                        print("\n⚠️  Password change required!")
                        if self._handle_password_change(username):
                            print("✅ Password changed successfully")
                        else:
                            print("❌ Password change failed")
                            return False
                    
                    # Show session info
                    session_info = self.session_manager.get_session_info()
                    if session_info:
                        print(f"🕐 Session expires in {session_info['time_left_hours']} hours")
                    
                    print()
                    return True
                else:
                    print(f"❌ {message}")
                    attempts += 1
                    
                    if attempts < max_attempts:
                        print(f"Try again ({max_attempts - attempts} attempts remaining)")
                        print()
                
            except KeyboardInterrupt:
                print("\n\nLogin cancelled by user")
                return False
            except Exception as e:
                print(f"❌ Login error: {e}")
                attempts += 1
        
        print("❌ Maximum login attempts exceeded")
        return False
    
    def _handle_password_change(self, username: str) -> bool:
        """Handle password change flow."""
        print("\n" + "=" * 40)
        print("PASSWORD CHANGE REQUIRED")
        print("=" * 40)
        print(self.password_validator.get_requirements_text())
        print()
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                new_password = getpass.getpass("New password: ")
                if not new_password:
                    print("❌ Password cannot be empty")
                    continue
                
                # Validate password
                is_valid, errors = self.password_validator.validate(new_password)
                if not is_valid:
                    print("❌ Password does not meet requirements:")
                    for error in errors:
                        print(f"   • {error}")
                    attempts += 1
                    continue
                
                # Confirm password
                confirm_password = getpass.getpass("Confirm new password: ")
                if new_password != confirm_password:
                    print("❌ Passwords do not match")
                    attempts += 1
                    continue
                
                # Show password strength
                strength, score, suggestions = PasswordStrengthMeter.assess_strength(new_password)
                print(f"Password strength: {strength} ({score}/100)")
                if suggestions:
                    print("Suggestions:", ", ".join(suggestions))
                
                # Update password
                password_hash = self.password_hasher.hash_password(new_password)
                if self.db.update_password(username, password_hash):
                    return True
                else:
                    print("❌ Failed to update password")
                    return False
                
            except KeyboardInterrupt:
                print("\nPassword change cancelled")
                return False
            except Exception as e:
                print(f"❌ Error changing password: {e}")
                attempts += 1
        
        print("❌ Maximum password change attempts exceeded")
        return False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.session_manager.is_authenticated()
    
    def get_current_user(self) -> Optional[str]:
        """Get currently authenticated username."""
        return self.session_manager.get_current_user()
    
    def logout(self):
        """Logout current user."""
        username = self.get_current_user()
        if username:
            self.session_manager.logout()
            print(f"👋 Goodbye, {username}!")
    
    # Admin functions
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Create a new user (admin function)."""
        # Validate username
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if self.db.user_exists(username):
            return False, "Username already exists"
        
        # Validate password
        is_valid, errors = self.password_validator.validate(password)
        if not is_valid:
            return False, "Password validation failed: " + "; ".join(errors)
        
        # Hash password and create user
        password_hash = self.password_hasher.hash_password(password)
        success = self.db.create_user(username, password_hash)
        
        if success:
            return True, f"User '{username}' created successfully"
        else:
            return False, "Failed to create user"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user (admin function)."""
        if username == "admin":
            return False, "Cannot delete admin user"
        
        if not self.db.user_exists(username):
            return False, "User does not exist"
        
        success = self.db.delete_user(username)
        if success:
            return True, f"User '{username}' deleted successfully"
        else:
            return False, "Failed to delete user"
    
    def change_user_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """Change password for a user (admin function)."""
        if not self.db.user_exists(username):
            return False, "User does not exist"
        
        # Validate password
        is_valid, errors = self.password_validator.validate(new_password)
        if not is_valid:
            return False, "Password validation failed: " + "; ".join(errors)
        
        # Update password
        password_hash = self.password_hasher.hash_password(new_password)
        success = self.db.update_password(username, password_hash)
        
        if success:
            return True, f"Password changed for user '{username}'"
        else:
            return False, "Failed to change password"
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin function)."""
        users = self.db.list_users()
        
        # Add additional info
        for user in users:
            # Convert datetime strings to more readable format
            if user['created_at']:
                created = datetime.fromisoformat(user['created_at'])
                user['created_at_readable'] = created.strftime("%Y-%m-%d %H:%M")
            
            if user['password_expires_at']:
                expires = datetime.fromisoformat(user['password_expires_at'])
                user['password_expires_readable'] = expires.strftime("%Y-%m-%d")
                
                # Check if password is expired or expiring soon
                days_until_expiry = (expires - datetime.now()).days
                if days_until_expiry < 0:
                    user['password_status'] = "EXPIRED"
                elif days_until_expiry < 30:
                    user['password_status'] = f"EXPIRES IN {days_until_expiry} DAYS"
                else:
                    user['password_status'] = "OK"
            
            if user['last_login']:
                last_login = datetime.fromisoformat(user['last_login'])
                user['last_login_readable'] = last_login.strftime("%Y-%m-%d %H:%M")
            else:
                user['last_login_readable'] = "Never"
        
        return users
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get authentication system information."""
        return {
            'total_users': self.db.get_user_count(),
            'current_user': self.get_current_user(),
            'session_info': self.session_manager.get_session_info(),
            'is_authenticated': self.is_authenticated()
        }