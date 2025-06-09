"""
JWT service for token generation and validation
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from ..config.settings import settings

logger = logging.getLogger(__name__)


class JWTService:
    """Service for JWT token operations"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = 7  # Default refresh token expiry
        self.issuer = "product-catalog-service"
        self.audience = "product-catalog-users"
    
    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        username: str,
        roles: List[str],
        permissions: List[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token with user information"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),
            "email": email,
            "username": username,
            "roles": roles,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": expire,
            "iss": self.issuer,
            "aud": self.audience,
            "type": "access"
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created access token for user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def create_refresh_token(
        self,
        user_id: UUID,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_id),
            "iat": datetime.utcnow(),
            "exp": expire,
            "iss": self.issuer,
            "aud": self.audience,
            "type": "refresh"
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Created refresh token for user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience
            )
            
            # Validate required fields
            if "sub" not in payload:
                logger.warning("Token missing 'sub' claim")
                return None
            
            if "type" not in payload:
                logger.warning("Token missing 'type' claim")
                return None
            
            logger.debug(f"Successfully verified token for user {payload['sub']}")
            return payload
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTClaimsError as e:
            logger.warning(f"Token claims error: {e}")
            return None
        except JWTError as e:
            logger.warning(f"JWT error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token and return payload"""
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != "access":
            logger.warning("Token is not an access token")
            return None
        
        return payload
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify refresh token and return payload"""
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None
        
        return payload
    
    def get_user_id_from_token(self, token: str) -> Optional[UUID]:
        """Extract user ID from token"""
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        try:
            user_id = UUID(payload["sub"])
            return user_id
        except (ValueError, KeyError):
            logger.warning("Invalid user ID in token")
            return None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiry time"""
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        try:
            exp_timestamp = payload["exp"]
            return datetime.fromtimestamp(exp_timestamp)
        except (KeyError, ValueError):
            logger.warning("Invalid expiry time in token")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        expiry = self.get_token_expiry(token)
        
        if not expiry:
            return True
        
        return datetime.utcnow() > expiry
    
    def get_token_type(self, token: str) -> Optional[str]:
        """Get token type (access or refresh)"""
        payload = self.verify_token(token)
        
        if not payload:
            return None
        
        return payload.get("type")
    
    def extract_bearer_token(self, authorization_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        
        if len(parts) != 2:
            return None
        
        scheme, token = parts
        
        if scheme.lower() != "bearer":
            return None
        
        return token
    
    def create_token_pair(
        self,
        user_id: UUID,
        email: str,
        username: str,
        roles: List[str],
        permissions: List[str]
    ) -> Dict[str, str]:
        """Create both access and refresh tokens"""
        access_token = self.create_access_token(
            user_id=user_id,
            email=email,
            username=username,
            roles=roles,
            permissions=permissions
        )
        
        refresh_token = self.create_refresh_token(user_id=user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging)"""
        try:
            payload = jwt.get_unverified_claims(token)
            return payload
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")
            return None
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get comprehensive token information"""
        payload = self.verify_token(token)
        
        if not payload:
            return {
                "valid": False,
                "error": "Invalid or expired token"
            }
        
        try:
            exp_timestamp = payload.get("exp")
            iat_timestamp = payload.get("iat")
            
            info = {
                "valid": True,
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "username": payload.get("username"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "token_type": payload.get("type"),
                "issuer": payload.get("iss"),
                "audience": payload.get("aud"),
                "issued_at": datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None,
                "expires_at": datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None,
                "is_expired": self.is_token_expired(token)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return {
                "valid": False,
                "error": f"Error processing token: {str(e)}"
            }


# Global JWT service instance
_jwt_service: Optional[JWTService] = None


def get_jwt_service() -> JWTService:
    """Get or create JWT service instance"""
    global _jwt_service
    
    if _jwt_service is None:
        _jwt_service = JWTService()
    
    return _jwt_service