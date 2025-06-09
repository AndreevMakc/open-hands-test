"""
Email value object

Represents and validates email addresses.
"""

import re
from typing import Any


class Email:
    """Email value object with validation"""
    
    # RFC 5322 compliant email regex (simplified)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("Email cannot be empty")
        
        # Normalize email (lowercase and strip)
        normalized_value = value.strip().lower()
        
        if not self._is_valid_email(normalized_value):
            raise ValueError(f"Invalid email format: {value}")
        
        self._value = normalized_value
    
    @property
    def value(self) -> str:
        """Get email value"""
        return self._value
    
    @property
    def local_part(self) -> str:
        """Get local part of email (before @)"""
        return self._value.split('@')[0]
    
    @property
    def domain(self) -> str:
        """Get domain part of email (after @)"""
        return self._value.split('@')[1]
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        if not self.EMAIL_PATTERN.match(email):
            return False
        
        # Additional checks
        local, domain = email.split('@')
        
        # Local part checks
        if len(local) > 64:  # RFC 5321 limit
            return False
        
        if local.startswith('.') or local.endswith('.'):
            return False
        
        if '..' in local:
            return False
        
        # Domain part checks
        if len(domain) > 253:
            return False
        
        if domain.startswith('.') or domain.endswith('.'):
            return False
        
        if '..' in domain:
            return False
        
        return True
    
    def is_same_domain(self, other: 'Email') -> bool:
        """Check if two emails have the same domain"""
        return self.domain == other.domain
    
    def mask(self) -> str:
        """Return masked email for privacy"""
        local = self.local_part
        domain = self.domain
        
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"Email('{self._value}')"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __lt__(self, other: 'Email') -> bool:
        return self._value < other._value