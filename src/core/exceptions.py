"""
Custom exceptions for ResellerOS.
"""


class ResellerOSException(Exception):
    """Base exception for all ResellerOS errors."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(ResellerOSException):
    """Database operation failed."""
    pass


class ValidationError(ResellerOSException):
    """Data validation failed."""
    pass


class NotFoundError(ResellerOSException):
    """Requested resource not found."""
    pass


class DuplicateError(ResellerOSException):
    """Resource already exists."""
    pass


class AuthenticationError(ResellerOSException):
    """Authentication failed."""
    pass


class AuthorizationError(ResellerOSException):
    """User not authorized for this action."""
    pass


class EbayAPIError(ResellerOSException):
    """eBay API request failed."""
    pass


class EbayAuthError(ResellerOSException):
    """eBay authentication/authorization failed."""
    pass


class EbayRateLimitError(ResellerOSException):
    """eBay API rate limit exceeded."""
    pass


class OllamaError(ResellerOSException):
    """Ollama AI service error."""
    pass


class OllamaUnavailableError(ResellerOSException):
    """Ollama service is not available."""
    pass


class FileUploadError(ResellerOSException):
    """File upload failed."""
    pass


class InvalidFileTypeError(ResellerOSException):
    """Invalid file type for upload."""
    pass


class FileSizeLimitError(ResellerOSException):
    """File size exceeds limit."""
    pass


class BackupError(ResellerOSException):
    """Backup operation failed."""
    pass


class ConfigurationError(ResellerOSException):
    """Configuration error."""
    pass


class ServiceUnavailableError(ResellerOSException):
    """Service temporarily unavailable."""
    pass


class ExternalServiceError(ResellerOSException):
    """External service error."""
    pass
