"""
Configuration validation and management for BharatLaw AI
Ensures all required environment variables are set and valid
"""

import os
from typing import List, Optional
from pydantic import BaseModel, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AppConfig(BaseModel):
    """Application configuration with validation"""

    # Required security settings
    secret_key: str
    database_url: str

    # API configuration
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    # Admin configuration
    admin_emails: List[str] = []

    # Performance settings
    max_concurrent_streams: int = 3

    # External service configurations
    openrouter_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "bharatlaw-index"

    # Email configuration
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None

    # Security configuration
    allowed_origins: List[str] = []
    allowed_hosts: List[str] = []

    # OAuth configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        if v == 'super-secret-key-that-is-not-safe-for-prod':
            raise ValueError('Please set a secure SECRET_KEY for production')
        return v

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('DATABASE_URL is required')
        return v

    @validator('max_concurrent_streams')
    def validate_max_streams(cls, v):
        if v < 1 or v > 10:
            raise ValueError('MAX_CONCURRENT_STREAMS must be between 1 and 10')
        return v

    @validator('admin_emails')
    def validate_admin_emails(cls, v):
        """Validate admin email format"""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for email in v:
            if not email_pattern.match(email):
                raise ValueError(f'Invalid email format: {email}')
        return v

    @validator('allowed_origins', 'allowed_hosts')
    def validate_lists(cls, v):
        """Ensure lists are not empty and contain valid values"""
        if not v or len(v) == 0:
            raise ValueError('List cannot be empty')
        return [item.strip() for item in v if item.strip()]


def load_config() -> AppConfig:
    """Load and validate application configuration from environment variables"""

    # Parse admin emails
    admin_emails_raw = os.getenv("ADMIN_EMAILS", "")
    admin_emails = [email.strip() for email in admin_emails_raw.split(",") if email.strip()] if admin_emails_raw else []

    config_data = {
        "secret_key": os.getenv("SECRET_KEY"),
        "database_url": os.getenv("DATABASE_URL"),
        "api_base_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "admin_emails": admin_emails,
        "max_concurrent_streams": int(os.getenv("MAX_CONCURRENT_STREAMS", "3")),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "pinecone_api_key": os.getenv("PINECONE_API_KEY"),
        "pinecone_environment": os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws"),
        "pinecone_index_name": os.getenv("PINECONE_INDEX_NAME", "bharatlaw-index"),
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME"),
        "smtp_password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("FROM_EMAIL"),
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "github_client_id": os.getenv("GITHUB_CLIENT_ID"),
        "github_client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://bharatlawainew-production.up.railway.app").split(",") if os.getenv("ALLOWED_ORIGINS") else ["http://localhost:5173", "http://127.0.0.1:5173", "https://bharatlawainew-production.up.railway.app"],
        "allowed_hosts": os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,bharatlawainew-production.up.railway.app").split(",") if os.getenv("ALLOWED_HOSTS") else ["localhost", "127.0.0.1", "bharatlawainew-production.up.railway.app"],
    }

    try:
        config = AppConfig(**config_data)
        print("✅ Configuration validation successful")
        return config
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        raise


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_config_summary() -> dict:
    """Get a summary of current configuration for debugging/monitoring"""
    config = get_config()

    return {
        "environment": {
            "database_configured": bool(config.database_url),
            "api_base_url": config.api_base_url,
            "frontend_url": config.frontend_url,
        },
        "security": {
            "secret_key_configured": bool(config.secret_key),
            "admin_emails_count": len(config.admin_emails),
            "oauth_google": bool(config.google_client_id),
            "oauth_github": bool(config.github_client_id),
        },
        "external_services": {
            "openrouter_configured": bool(config.openrouter_api_key),
            "pinecone_configured": bool(config.pinecone_api_key),
            "pinecone_index": config.pinecone_index_name,
            "email_configured": bool(config.smtp_server and config.smtp_username),
        },
        "performance": {
            "max_concurrent_streams": config.max_concurrent_streams,
            "allowed_origins_count": len(config.allowed_origins),
            "allowed_hosts_count": len(config.allowed_hosts),
        }
    }


def validate_config_for_environment() -> list:
    """Validate configuration for the current environment and return warnings"""
    config = get_config()
    warnings = []

    # Check for development vs production issues
    if "localhost" in config.api_base_url and "railway" not in config.api_base_url:
        warnings.append("⚠️  Using localhost API URL - ensure backend is running")

    if not config.openrouter_api_key:
        warnings.append("⚠️  OPENROUTER_API_KEY not configured - RAG features may not work")

    if not config.pinecone_api_key:
        warnings.append("⚠️  PINECONE_API_KEY not configured - vector search may not work")

    if not config.admin_emails:
        warnings.append("⚠️  No admin emails configured - admin features will be disabled")

    if len(config.secret_key) < 32:
        warnings.append("❌ SECRET_KEY is too short - must be at least 32 characters")

    return warnings