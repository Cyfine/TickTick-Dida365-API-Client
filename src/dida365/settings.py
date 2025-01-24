"""Configuration settings for the Dida365 client."""
import os
from pathlib import Path
from typing import ClassVar, Dict, Optional

import tomli
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from .config import ServiceType
from .logger import setup_logging

# Load environment variables from .env file
load_dotenv(override=True)


def load_pyproject_settings() -> dict:
    """Load settings from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)
            return pyproject.get("tool", {}).get("dida365", {})
    return {}


# Load settings once at module level
PYPROJECT_SETTINGS = load_pyproject_settings()
ENV_PREFIX = PYPROJECT_SETTINGS.get("env_prefix", "DIDA365_")


class RequestTimeoutConfig(BaseModel):
    """Request timeout configuration."""
    connect: float = Field(default=10.0, description="Connection timeout in seconds")
    read: float = Field(default=30.0, description="Read timeout in seconds")
    write: float = Field(default=30.0, description="Write timeout in seconds")
    pool: float = Field(default=5.0, description="Pool timeout in seconds")


class Settings(BaseSettings):
    """Application settings loaded from environment variables and pyproject.toml."""

    # Client credentials
    client_id: str = Field(
        default="",
        description="OAuth2 client ID",
        validation_alias=f"{ENV_PREFIX}CLIENT_ID"
    )
    client_secret: str = Field(
        default="",
        description="OAuth2 client secret",
        validation_alias=f"{ENV_PREFIX}CLIENT_SECRET"
    )
    redirect_uri: Optional[str] = Field(
        default=None,
        description="OAuth2 redirect URI",
        validation_alias=f"{ENV_PREFIX}REDIRECT_URI"
    )
    access_token: Optional[str] = Field(
        default=None,
        description="OAuth2 access token",
        validation_alias=f"{ENV_PREFIX}ACCESS_TOKEN"
    )

    # Service configuration
    service_type: ServiceType = Field(
        default=PYPROJECT_SETTINGS.get("default_service", ServiceType.DIDA365),
        description="Service type (dida365 or ticktick)", 
        validation_alias=f"{ENV_PREFIX}SERVICE_TYPE",
    )
 
    custom_base_url: Optional[str] = Field(
        default=None,
        description="Custom API base URL",
        validation_alias=f"{ENV_PREFIX}BASE_URL"
    )

    # Token storage
    token_file: Path = Field(
        default=Path(PYPROJECT_SETTINGS.get("token_file", ".dida365_token.json")),
        description="Path to token storage file",
        validation_alias=f"{ENV_PREFIX}TOKEN_FILE"
    )

    # Logging configuration
    log_level: str = Field(
        default=PYPROJECT_SETTINGS.get("log_level", "INFO"),
        description="Logging level",
        validation_alias=f"{ENV_PREFIX}LOG_LEVEL"
    )
    log_format: str = Field(
        default=PYPROJECT_SETTINGS.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        description="Log message format",
        validation_alias=f"{ENV_PREFIX}LOG_FORMAT"
    )
    log_date_format: str = Field(
        default=PYPROJECT_SETTINGS.get("log_date_format", "%Y-%m-%d %H:%M:%S"),
        description="Log date format",
        validation_alias=f"{ENV_PREFIX}LOG_DATE_FORMAT"
    )
    log_file: Optional[str] = Field(
        default=PYPROJECT_SETTINGS.get("log_file", None),
        description="Log file path",
        validation_alias=f"{ENV_PREFIX}LOG_FILE"
    )
    debug: bool = Field(
        default=PYPROJECT_SETTINGS.get("debug", False),
        description="Enable debug mode",
        validation_alias=f"{ENV_PREFIX}DEBUG"
    )

    # Request configuration
    request_timeout: RequestTimeoutConfig = Field(
        default_factory=lambda: RequestTimeoutConfig(
            **PYPROJECT_SETTINGS.get("request_timeout", {})
        ),
        description="Request timeout settings"
    )
    max_retries: int = Field(
        default=PYPROJECT_SETTINGS.get("max_retries", 3),
        description="Maximum number of request retries",
        validation_alias=f"{ENV_PREFIX}MAX_RETRIES"
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields in environment variables
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configure logging based on settings
        setup_logging(
            level=self.log_level.upper() if self.debug else "INFO",
            log_format=self.log_format,
            date_format=self.log_date_format,
            log_file=self.log_file
        )


# Global settings instance
settings = Settings() 