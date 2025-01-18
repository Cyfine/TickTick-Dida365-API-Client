"""HTTP client module for making API requests."""
from functools import wraps
from typing import Any, Dict, Optional, Type, TypeVar, List
import json

import httpx
from httpx import Timeout

from .config import ApiConfig
from .exceptions import ApiError, AuthenticationError, NotFoundError, RateLimitError, ValidationError
from .logger import logger

T = TypeVar("T")

#The exact headers that work with the API
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

# Default timeouts (in seconds)
DEFAULT_TIMEOUT = Timeout(
    connect=10.0,    # Maximum time to wait for a connection
    read=30.0,       # Maximum time to wait for data
    write=30.0,      # Maximum time to wait for data to be sent
    pool=5.0         # Maximum time to wait for a connection from the pool
)


def retry_on_rate_limit(func):
    """Decorator to retry requests when rate limit is hit."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper


class HttpClient:
    def __init__(
        self,
        config: ApiConfig,
        timeout: Optional[Timeout] = None,
        max_retries: int = 3
    ):
        """Initialize the HTTP client.
        
        Args:
            config: API configuration
            timeout: Optional custom timeout settings
            max_retries: Maximum number of retries for failed requests
        """
        self.config = config
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.max_retries = max_retries
        
        # Initialize session with proper settings
        self._session = httpx.AsyncClient(
            timeout=self.timeout,
            headers=DEFAULT_HEADERS.copy(),
            follow_redirects=True
        )
        self.token = None

    async def set_token(self, token: str):
        """Set the access token for authenticated requests."""
        if not token:
            raise ValidationError("Token cannot be empty")
        self.token = token

    async def close(self):
        """Close the HTTP session."""
        if self._session:
            await self._session.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the request, including auth if token exists."""
        headers = DEFAULT_HEADERS.copy()
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _log_request(self, url: str, method: str, headers: Dict[str, str], json_data: Optional[Dict] = None):
        """Log request details for debugging."""
        logger.debug("API Request Details:")
        logger.debug(f"URL: {url}")
        logger.debug(f"Method: {method}")
        logger.debug(f"Headers: {headers}")
        if json_data:
            logger.debug(f"JSON Data: {json_data}")

    def _log_response(self, response: httpx.Response):
        """Log response details for debugging."""
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        if response.content:
            logger.debug(f"Response Body: {response.text}")

    def _handle_error_response(self, e: httpx.HTTPStatusError, url: str) -> None:
        """Handle error responses from the API."""
        error_data = {}
        try:
            error_data = e.response.json()
        except json.JSONDecodeError:
            error_data = {"errorMessage": str(e)}

        error_msg = error_data.get("errorMessage", str(e))
        error_code = error_data.get("errorCode")
        error_id = error_data.get("errorId")

        if e.response.status_code == 401:
            raise AuthenticationError(
                message="Authentication failed",
                error_code=error_code,
                error_id=error_id
            ) from e
        elif e.response.status_code == 404:
            raise NotFoundError(
                message=f"Resource not found: {url}",
                error_code=error_code,
                error_id=error_id
            ) from e
        elif e.response.status_code == 429:
            raise RateLimitError(
                message="Rate limit exceeded",
                error_code=error_code,
                error_id=error_id
            ) from e
        elif e.response.status_code == 400:
            raise ValidationError(
                message=error_msg,
                error_code=error_code,
                error_id=error_id
            ) from e
        else:
            raise ApiError(
                message=f"API request failed: {error_msg}",
                error_code=error_code,
                error_id=error_id
            ) from e

    def _parse_response(self, data: Any, model: Optional[Type[T]]) -> Optional[T]:
        """Parse response data according to the model type."""
        if model is not None:
            if isinstance(data, list):
                # Handle List[T] types
                if hasattr(model, '__origin__') and model.__origin__ is list:
                    item_type = model.__args__[0]
                    return [item_type(**item) for item in data]
                return [model(**item) for item in data]
            return model(**data)
        return None

    @retry_on_rate_limit
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        model: Optional[Type[T]] = None,
    ) -> Optional[T]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON request body
            model: Pydantic model for response parsing

        Returns:
            Parsed response data if model is provided, None otherwise

        Raises:
            ApiError: For API-related errors
            AuthenticationError: For authentication errors
            NotFoundError: When resource is not found
            RateLimitError: When rate limit is exceeded
            ValidationError: When request validation fails
            httpx.HTTPError: For other HTTP errors
        """
        if not endpoint:
            raise ValidationError("Endpoint cannot be empty")

        url = self.config.get_api_url(endpoint)
        headers = self._get_headers()
        
        self._log_request(url, method, headers, json_data)

        try:
            response = await self._session.request(
                method,
                url,
                params=params,
                json=json_data,
                headers=headers,
            )
            self._log_response(response)

            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return None

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise ApiError(f"Invalid JSON response: {str(e)}")

            return self._parse_response(data, model)

        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as e:
            raise ApiError("Request timed out")
        except httpx.ConnectError:
            raise ApiError("Failed to connect to server")
        except httpx.HTTPStatusError as e:
            self._handle_error_response(e, url)
        except Exception as e:
            raise ApiError(f"Unexpected error: {str(e)}")

    async def get(self, endpoint: str, *, model: Optional[Type[T]] = None) -> Optional[T]:
        """Send GET request."""
        return await self._make_request("GET", endpoint, model=model)

    async def post(
        self,
        endpoint: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        model: Optional[Type[T]] = None,
    ) -> Optional[T]:
        """Send POST request."""
        return await self._make_request("POST", endpoint, json_data=json_data, model=model)

    async def put(
        self,
        endpoint: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        model: Optional[Type[T]] = None,
    ) -> Optional[T]:
        """Send PUT request."""
        return await self._make_request("PUT", endpoint, json_data=json_data, model=model)

    async def delete(self, endpoint: str) -> None:
        """Send DELETE request."""
        await self._make_request("DELETE", endpoint) 