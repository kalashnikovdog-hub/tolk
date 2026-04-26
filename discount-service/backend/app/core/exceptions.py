"""
Custom exceptions for the application
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = None,
        headers: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.headers = headers
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception"""
    
    def __init__(self, resource: str = "Resource", item_id: int = None):
        message = f"{resource} not found"
        if item_id:
            message += f": {item_id}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception"""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            message="Unauthorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(AppException):
    """Forbidden access exception"""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            message="Forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestException(AppException):
    """Bad request exception"""
    
    def __init__(self, detail: str = "Invalid request data"):
        super().__init__(
            message="Bad Request",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate resource)"""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            message="Conflict",
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class RateLimitExceededException(AppException):
    """Rate limit exceeded exception"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)}
        )


class DatabaseException(AppException):
    """Database operation exception"""
    
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            message="Database Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class CacheException(AppException):
    """Cache operation exception"""
    
    def __init__(self, detail: str = "Cache error occurred"):
        super().__init__(
            message="Cache Error",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class AppExceptionHandlers:
    """Register exception handlers for FastAPI app"""
    
    @staticmethod
    def register_handlers(app: FastAPI):
        """Register all exception handlers"""
        
        @app.exception_handler(AppException)
        async def app_exception_handler(request: Request, exc: AppException):
            logger.warning(f"AppException: {exc.message} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "message": exc.message,
                    "detail": exc.detail
                },
                headers=exc.headers
            )
        
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            logger.warning(f"Validation error: {exc.errors()}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "message": "Validation Error",
                    "detail": exc.errors()
                }
            )
        
        @app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
            logger.error(f"Database error: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Database Error",
                    "detail": "An internal database error occurred"
                }
            )
        
        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Internal Server Error",
                    "detail": "An unexpected error occurred"
                }
            )
