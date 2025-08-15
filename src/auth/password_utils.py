"""
Password utilities for authentication system.

Provides password validation, hashing, and security features.
"""

import re
import bcrypt
import secrets
from typing import Tuple, List


class PasswordValidator:
    """Validates password strength according to security requirements."""
    
    # Password requirements
    MIN_LENGTH = 8
    REQUIRED_UPPERCASE = 1
    REQUIRED_SPECIAL = 1
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def validate(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against security requirements.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        # Check for uppercase letters
        uppercase_count = sum(1 for c in password if c.isupper())
        if uppercase_count < cls.REQUIRED_UPPERCASE:
            errors.append(f"Password must contain at least {cls.REQUIRED_UPPERCASE} uppercase letter(s)")
        
        # Check for special characters
        special_count = sum(1 for c in password if c in cls.SPECIAL_CHARS)
        if special_count < cls.REQUIRED_SPECIAL:
            errors.append(f"Password must contain at least {cls.REQUIRED_SPECIAL} special character(s)")
            errors.append(f"Special characters: {cls.SPECIAL_CHARS}")
        
        # Check for common weak patterns
        if password.lower() in ['password', '12345678', 'admin123', 'qwerty123']:
            errors.append("Password is too common and easily guessable")
        
        # Check for repeated characters (more than 3 in a row)
        if re.search(r'(.)\1{3,}', password):
            errors.append("Password cannot contain more than 3 consecutive identical characters")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_requirements_text(cls) -> str:
        """Get human-readable password requirements."""
        return f"""Password Requirements:
• At least {cls.MIN_LENGTH} characters long
• At least {cls.REQUIRED_UPPERCASE} uppercase letter
• At least {cls.REQUIRED_SPECIAL} special character ({cls.SPECIAL_CHARS})
• Cannot be a common password
• Cannot have more than 3 consecutive identical characters"""


class PasswordHasher:
    """Handles password hashing and verification using bcrypt."""
    
    # bcrypt work factor (cost parameter)
    ROUNDS = 12
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as string
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=cls.ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Previously hashed password
            
        Returns:
            True if password matches hash
        """
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def generate_secure_password(cls, length: int = 12) -> str:
        """
        Generate a secure random password that meets requirements.
        
        Args:
            length: Password length (minimum 8)
            
        Returns:
            Generated password
        """
        if length < cls.MIN_LENGTH:
            length = cls.MIN_LENGTH
        
        # Character pools
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = PasswordValidator.SPECIAL_CHARS
        
        # Ensure we have at least one from each required category
        password_chars = []
        
        # Add required characters
        password_chars.append(secrets.choice(uppercase))  # At least 1 uppercase
        password_chars.append(secrets.choice(special))    # At least 1 special
        
        # Fill remaining length with random characters from all pools
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - len(password_chars)):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the password characters
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)


class PasswordStrengthMeter:
    """Provides password strength assessment."""
    
    @classmethod
    def assess_strength(cls, password: str) -> Tuple[str, int, List[str]]:
        """
        Assess password strength.
        
        Returns:
            Tuple of (strength_label, score_0_to_100, suggestions)
        """
        score = 0
        suggestions = []
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        elif len(password) >= 6:
            score += 10
            suggestions.append("Use at least 8 characters")
        else:
            suggestions.append("Password is too short (minimum 8 characters)")
        
        # Character variety scoring
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in PasswordValidator.SPECIAL_CHARS for c in password)
        
        variety_score = sum([has_lower, has_upper, has_digit, has_special]) * 15
        score += variety_score
        
        if not has_upper:
            suggestions.append("Add uppercase letters")
        if not has_special:
            suggestions.append("Add special characters")
        if not has_digit:
            suggestions.append("Consider adding numbers")
        
        # Length bonus
        if len(password) >= 12:
            score += 20
        elif len(password) >= 10:
            score += 10
        
        # Penalty for common patterns
        if re.search(r'123|abc|qwe|password', password.lower()):
            score -= 20
            suggestions.append("Avoid common patterns")
        
        # Cap score at 100
        score = min(100, max(0, score))
        
        # Determine strength label
        if score >= 80:
            strength = "Very Strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Medium"
        elif score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return strength, score, suggestions