"""API exception classes."""

class ApiError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, error_code: str = None, error_id: str = None):
        self.message = message
        self.error_code = error_code
        self.error_id = error_id
        super().__init__(self.format_message())

    def format_message(self) -> str:
        parts = [self.message]
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        if self.error_id:
            parts.append(f"Error ID: {self.error_id}")
        return " | ".join(parts)


class AuthenticationError(ApiError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ApiError):
    """Raised when a resource is not found."""
    pass


class RateLimitError(ApiError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(ApiError):
    """Raised when request validation fails."""
    pass 