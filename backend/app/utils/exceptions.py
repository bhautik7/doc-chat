class AppError(Exception):
    """Base class for errors that map to a well-defined API response."""

    status_code = 500
    default_message = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    default_message = "Resource not found"


class ConflictError(AppError):
    status_code = 400
    default_message = "Request conflicts with existing data"


class DocumentProcessingError(AppError):
    status_code = 422
    default_message = "Document could not be processed"


class StorageError(AppError):
    status_code = 502
    default_message = "Document storage is currently unavailable"


class VectorStoreError(AppError):
    status_code = 503
    default_message = "Document search is currently unavailable"


class LLMError(AppError):
    status_code = 502
    default_message = "The answer service is currently unavailable"
