"""Configuration module for Dida365/TickTick API client."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

from .exceptions import ValidationError
from .logger import logger


class ServiceType(str, Enum):
    """Available service types for the API."""

    DIDA365 = "dida365"  # Chinese version
    TICKTICK = "ticktick"  # International version


def validate_url(url: str, allow_custom: bool = True) -> bool:
    """Validate URL format.
    
    Args:
        url: URL to validate
        allow_custom: Whether to allow custom domains
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        valid_scheme = result.scheme in ("http", "https")
        if not allow_custom:
            valid_domain = result.netloc in ("api.dida365.com", "api.ticktick.com", 
                                           "dida365.com", "ticktick.com")
            return valid_scheme and valid_domain
        return valid_scheme and result.netloc
    except Exception:
        return False


@dataclass
class ApiConfig:
    """API configuration settings."""

    service_type: ServiceType = ServiceType.DIDA365
    api_version: str = "v1"
    custom_base_url: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.custom_base_url and not validate_url(self.custom_base_url):
            raise ValidationError(f"Invalid custom base URL: {self.custom_base_url}")
        
        if not self.api_version.startswith("v"):
            logger.warning(f"API version {self.api_version} might be invalid - should start with 'v'")

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        if self.custom_base_url:
            return self.custom_base_url.rstrip("/")

        if self.service_type == ServiceType.DIDA365:
            return "https://api.dida365.com"
        return "https://api.ticktick.com"

    @property
    def auth_url(self) -> str:
        """Get the authorization URL."""
        domain = "dida365.com" if self.service_type == ServiceType.DIDA365 else "ticktick.com"
        url = f"https://{domain}/oauth/authorize"
        if not validate_url(url, allow_custom=False):
            raise ValidationError(f"Invalid auth URL generated: {url}")
        return url

    @property
    def token_url(self) -> str:
        """Get the token URL."""
        domain = "dida365.com" if self.service_type == ServiceType.DIDA365 else "ticktick.com"
        url = f"https://{domain}/oauth/token"
        if not validate_url(url, allow_custom=False):
            raise ValidationError(f"Invalid token URL generated: {url}")
        return url

    def get_api_url(self, endpoint: str) -> str:
        """
        Get the full API URL for a given endpoint.

        Args:
            endpoint: The API endpoint path.

        Returns:
            The complete API URL.

        Raises:
            ValidationError: If the resulting URL is invalid
        """
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/open/{self.api_version}/{endpoint}"
        
        if not validate_url(url, allow_custom=bool(self.custom_base_url)):
            raise ValidationError(f"Invalid API URL generated: {url}")
            
        return url 