"""Application-wide constants."""

# API routes
API_V1_PREFIX = "/api/v1"
AUTH_PREFIX = "/auths"
HEALTH_PREFIX = "/health"

# Error messages (moved from open_webui.constants)
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Invalid credentials",
    "INVALID_TOKEN": "Invalid or expired token",
    "UNAUTHORIZED": "Unauthorized",
    "USER_NOT_FOUND": "User not found",
    "USER_ALREADY_EXISTS": "User already exists",
    "INVALID_REQUEST": "Invalid request",
    "DATABASE_ERROR": "Database error",
    "FILE_NOT_FOUND": "File not found",
    "UPLOAD_FAILED": "Upload failed",
}

FEEDBACK_TYPES = ["positive", "negative", "neutral"]
