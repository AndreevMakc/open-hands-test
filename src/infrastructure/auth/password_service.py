"""
Password service for hashing and verification
"""

import logging
import secrets
import string
from typing import Optional

from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class PasswordService:
    """Service for password hashing and verification"""
    
    def __init__(self):
        # Configure password context with bcrypt
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Good balance of security and performance
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            hashed = self.pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        if not plain_password or not hashed_password:
            return False
        
        try:
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            logger.debug(f"Password verification: {'success' if is_valid else 'failed'}")
            return is_valid
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def needs_update(self, hashed_password: str) -> bool:
        """Check if password hash needs to be updated"""
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Error checking if password needs update: {e}")
            return False
    
    def generate_random_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        if length > 128:
            raise ValueError("Password length cannot exceed 128 characters")
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special_chars)
        ]
        
        # Fill the rest with random characters from all sets
        all_chars = lowercase + uppercase + digits + special_chars
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def validate_password_strength(self, password: str) -> dict:
        """Validate password strength and return detailed feedback"""
        if not password:
            return {
                "is_valid": False,
                "score": 0,
                "feedback": ["Password cannot be empty"]
            }
        
        feedback = []
        score = 0
        
        # Length check
        if len(password) < 8:
            feedback.append("Password must be at least 8 characters long")
        elif len(password) >= 8:
            score += 1
        
        if len(password) >= 12:
            score += 1
        
        # Character variety checks
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_lowercase:
            feedback.append("Password should contain lowercase letters")
        else:
            score += 1
        
        if not has_uppercase:
            feedback.append("Password should contain uppercase letters")
        else:
            score += 1
        
        if not has_digit:
            feedback.append("Password should contain numbers")
        else:
            score += 1
        
        if not has_special:
            feedback.append("Password should contain special characters")
        else:
            score += 1
        
        # Common patterns check
        if password.lower() in ["password", "123456", "qwerty", "admin"]:
            feedback.append("Password is too common")
            score = max(0, score - 2)
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            feedback.append("Avoid sequential characters (abc, 123)")
            score = max(0, score - 1)
        
        # Repeated characters check
        if self._has_repeated_chars(password):
            feedback.append("Avoid repeated characters (aaa, 111)")
            score = max(0, score - 1)
        
        # Determine strength level
        if score >= 6:
            strength = "strong"
        elif score >= 4:
            strength = "medium"
        elif score >= 2:
            strength = "weak"
        else:
            strength = "very_weak"
        
        is_valid = len(feedback) == 0 and score >= 4
        
        return {
            "is_valid": is_valid,
            "score": score,
            "strength": strength,
            "feedback": feedback,
            "requirements_met": {
                "min_length": len(password) >= 8,
                "has_lowercase": has_lowercase,
                "has_uppercase": has_uppercase,
                "has_digit": has_digit,
                "has_special": has_special
            }
        }
    
    def _has_sequential_chars(self, password: str, min_length: int = 3) -> bool:
        """Check for sequential characters"""
        password = password.lower()
        
        for i in range(len(password) - min_length + 1):
            substring = password[i:i + min_length]
            
            # Check for ascending sequence
            if all(ord(substring[j]) == ord(substring[j-1]) + 1 for j in range(1, len(substring))):
                return True
            
            # Check for descending sequence
            if all(ord(substring[j]) == ord(substring[j-1]) - 1 for j in range(1, len(substring))):
                return True
        
        return False
    
    def _has_repeated_chars(self, password: str, min_length: int = 3) -> bool:
        """Check for repeated characters"""
        for i in range(len(password) - min_length + 1):
            substring = password[i:i + min_length]
            if len(set(substring)) == 1:  # All characters are the same
                return True
        
        return False
    
    def generate_reset_token(self, length: int = 32) -> str:
        """Generate a secure token for password reset"""
        return secrets.token_urlsafe(length)
    
    def hash_reset_token(self, token: str) -> str:
        """Hash a reset token for storage"""
        return self.hash_password(token)
    
    def verify_reset_token(self, token: str, hashed_token: str) -> bool:
        """Verify a reset token against its hash"""
        return self.verify_password(token, hashed_token)


# Global password service instance
_password_service: Optional[PasswordService] = None


def get_password_service() -> PasswordService:
    """Get or create password service instance"""
    global _password_service
    
    if _password_service is None:
        _password_service = PasswordService()
    
    return _password_service