#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Natural Language CLI Entry Point for Universal Product Scraper
Run this for a user-friendly, conversational interface to the scraper.
"""

import sys
import io
import argparse
from pathlib import Path

# Set UTF-8 encoding for stdout to handle Hebrew characters
if sys.platform == "win32":
    # For Windows, reconfigure stdout to use UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.cli.natural_interface import NaturalLanguageCLI
    from src.auth.auth_manager import AuthManager
    
    def handle_admin_commands(args, auth_manager):
        """Handle admin commands."""
        if args.create_user:
            import getpass
            username = args.create_user
            print(f"Creating user: {username}")
            
            password = getpass.getpass("Enter password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                print("❌ Passwords do not match")
                return False
            
            success, message = auth_manager.create_user(username, password)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            return True
            
        elif args.delete_user:
            username = args.delete_user
            confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ")
            if confirm.lower() == 'yes':
                success, message = auth_manager.delete_user(username)
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
            else:
                print("User deletion cancelled")
            return True
            
        elif args.reset_password:
            import getpass
            username = args.reset_password
            print(f"Resetting password for user: {username}")
            
            password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            
            if password != confirm_password:
                print("❌ Passwords do not match")
                return False
            
            success, message = auth_manager.change_user_password(username, password)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            return True
            
        elif args.list_users:
            users = auth_manager.list_users()
            if not users:
                print("No users found")
            else:
                print("\n📋 User List")
                print("=" * 80)
                print(f"{'Username':<15} {'Created':<12} {'Last Login':<12} {'Password Status':<20}")
                print("-" * 80)
                
                for user in users:
                    print(f"{user['username']:<15} {user['created_at_readable']:<12} "
                          f"{user['last_login_readable']:<12} {user['password_status']:<20}")
                print()
            return True
        
        return False
    
    def main():
        """Main entry point."""
        # Parse command line arguments for admin functions
        parser = argparse.ArgumentParser(description='Universal Product Scraper CLI')
        parser.add_argument('--create-user', metavar='USERNAME', help='Create a new user')
        parser.add_argument('--delete-user', metavar='USERNAME', help='Delete an existing user')
        parser.add_argument('--reset-password', metavar='USERNAME', help='Reset password for a user')
        parser.add_argument('--list-users', action='store_true', help='List all users')
        
        args = parser.parse_args()
        
        # Initialize authentication manager
        auth_manager = AuthManager()
        
        # Handle admin commands (run without authentication)
        if any([args.create_user, args.delete_user, args.reset_password, args.list_users]):
            if handle_admin_commands(args, auth_manager):
                return  # Exit after handling admin command
        
        # Regular CLI flow - requires authentication
        print("🚀 Starting Universal Product Scraper...")
        print()
        
        # Authenticate user
        if not auth_manager.login_flow():
            print("❌ Authentication failed. Exiting...")
            sys.exit(1)
        
        # Start main CLI interface
        print("🚀 Starting Natural Language Interface...")
        cli = NaturalLanguageCLI()
        cli.start_interactive_session(auth_manager)
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory.")
    print("Also ensure bcrypt is installed: pip install bcrypt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 