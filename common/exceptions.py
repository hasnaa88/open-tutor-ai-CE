"""Domain-specific exceptions."""

from typing import Optional


class TutorAIException(Exception):
    """Base exception for all TutorAI errors."""

    message: str
    code: str

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(TutorAIException):
    """Raised when authentication fails."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Invalid credentials"
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(TutorAIException):
    """Raised when authorization fails."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Insufficient permissions"
        super().__init__(message, "AUTHORIZATION_ERROR")


class ValidationError(TutorAIException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundError(TutorAIException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, "NOT_FOUND")


class DatabaseError(TutorAIException):
    """Raised when database operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class FileOperationError(TutorAIException):
    """Raised when file operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "FILE_ERROR")
