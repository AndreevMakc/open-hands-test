from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://catalog_user:catalog_pass@localhost:5432/catalog_db",
        description="Database connection URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_max_connections: int = Field(default=20, description="Redis max connections")
    redis_socket_timeout: int = Field(default=5, description="Redis socket timeout")
    redis_socket_connect_timeout: int = Field(default=5, description="Redis socket connect timeout")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    project_name: str = Field(default="Product Catalog API", description="Project name")
    version: str = Field(default="0.1.0", description="API version")
    description: str = Field(
        default="Product Catalog Service with configurable attributes",
        description="API description"
    )
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["*"], description="Allowed CORS origins"
    )
    
    # Cache
    cache_ttl_categories: int = Field(
        default=3600, description="Categories cache TTL in seconds"
    )
    cache_ttl_category_tree: int = Field(
        default=1800, description="Category tree cache TTL in seconds"
    )
    cache_ttl_product_details: int = Field(
        default=900, description="Product details cache TTL in seconds"
    )
    cache_ttl_search_results: int = Field(
        default=300, description="Search results cache TTL in seconds"
    )
    cache_ttl_category_attributes: int = Field(
        default=3600, description="Category attributes cache TTL in seconds"
    )
    
    # Pagination
    default_page_size: int = Field(default=20, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")
    
    # Development
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on changes")
    
    # Authentication (optional for internal installations)
    auth_enabled: bool = Field(default=True, description="Enable authentication")
    
    # JWT Authentication Settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production-please-use-strong-key",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Password Settings
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase in password")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase in password")
    password_require_numbers: bool = Field(default=True, description="Require numbers in password")
    password_require_special: bool = Field(default=True, description="Require special characters in password")
    
    # Security Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Session Settings
    session_timeout_minutes: int = Field(default=60, description="Session timeout in minutes")
    max_login_attempts: int = Field(default=5, description="Maximum login attempts before lockout")
    lockout_duration_minutes: int = Field(default=15, description="Account lockout duration in minutes")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()