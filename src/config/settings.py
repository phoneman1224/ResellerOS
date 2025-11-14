"""
Application settings and configuration management.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="ResellerOS", env="APP_NAME")
    app_env: str = Field(default="production", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")

    # Database
    database_url: str = Field(default="sqlite:///./reselleros.db", env="DATABASE_URL")

    # API Server
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # eBay API
    ebay_client_id: Optional[str] = Field(default=None, env="EBAY_CLIENT_ID")
    ebay_client_secret: Optional[str] = Field(default=None, env="EBAY_CLIENT_SECRET")
    ebay_redirect_uri: str = Field(default="http://localhost:8080", env="EBAY_REDIRECT_URI")
    ebay_environment: str = Field(default="production", env="EBAY_ENVIRONMENT")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="phi3", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=30, env="OLLAMA_TIMEOUT")

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    # Backup Configuration
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_interval_hours: int = Field(default=24, env="BACKUP_INTERVAL_HOURS")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/reselleros.log", env="LOG_FILE")

    # File Upload Settings
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Backup Settings
    backup_dir: str = "backups"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        dirs = [
            self.upload_dir,
            self.backup_dir,
            Path(self.log_file).parent,
        ]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development" or self.debug

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def ebay_configured(self) -> bool:
        """Check if eBay API is configured."""
        return bool(self.ebay_client_id and self.ebay_client_secret)

    @property
    def ebay_auth_url(self) -> str:
        """Get eBay OAuth URL based on environment."""
        if self.ebay_environment.lower() == "sandbox":
            return "https://auth.sandbox.ebay.com/oauth2/authorize"
        return "https://auth.ebay.com/oauth2/authorize"

    @property
    def ebay_token_url(self) -> str:
        """Get eBay token URL based on environment."""
        if self.ebay_environment.lower() == "sandbox":
            return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        return "https://api.ebay.com/identity/v1/oauth2/token"

    @property
    def ebay_api_base_url(self) -> str:
        """Get eBay API base URL based on environment."""
        if self.ebay_environment.lower() == "sandbox":
            return "https://api.sandbox.ebay.com"
        return "https://api.ebay.com"


# Global settings instance
settings = Settings()
