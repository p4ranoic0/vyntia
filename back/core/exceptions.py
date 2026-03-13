"""Custom exception handlers and exception classes."""

import logging
from typing import Any, Dict, Optional
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
    ParseError
)
from .responses import APIResponse


logger = logging.getLogger(__name__)


class CustomException(Exception):
    """Base custom exception class."""
    
    def __init__(
        self,
        message: str = "Error en la operación",
        error_code: str = "CUSTOM_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessLogicError(CustomException):
    """Exception for business logic violations."""
    
    def __init__(
        self,
        message: str = "Error en la lógica de negocio",
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ResourceNotFoundError(CustomException):
    """Exception for resource not found errors."""
    
    def __init__(
        self,
        resource: str = "Recurso",
        resource_id: Optional[str] = None,
        error_code: str = "RESOURCE_NOT_FOUND"
    ):
        message = f"{resource} no encontrado"
        if resource_id:
            message += f" con ID: {resource_id}"
            
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "resource_id": resource_id}
        )


class DuplicateResourceError(CustomException):
    """Exception for duplicate resource errors."""
    
    def __init__(
        self,
        resource: str = "Recurso",
        field: Optional[str] = None,
        value: Optional[str] = None,
        error_code: str = "DUPLICATE_RESOURCE"
    ):
        message = f"{resource} ya existe"
        if field and value:
            message += f" con {field}: {value}"
            
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "field": field, "value": value}
        )


class InvalidOperationError(CustomException):
    """Exception for invalid operations."""
    
    def __init__(
        self,
        operation: str = "Operación",
        reason: Optional[str] = None,
        error_code: str = "INVALID_OPERATION"
    ):
        message = f"{operation} no válida"
        if reason:
            message += f": {reason}"
            
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"operation": operation, "reason": reason}
        )


class DatabaseError(CustomException):
    """Exception for database-related errors."""
    
    def __init__(
        self,
        message: str = "Error en la base de datos",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


def custom_exception_handler(exc, context):
    """Custom exception handler for DRF.
    
    Args:
        exc: The exception instance
        context: Context information about the exception
        
    Returns:
        Response: Unified error response
    """
    # Get the standard error response
    response = exception_handler(exc, context)
    
    # Log the exception
    logger.error(
        f"Exception in {context.get('view', 'Unknown view')}: {str(exc)}",
        exc_info=True,
        extra={
            'view': str(context.get('view', 'Unknown')),
            'request': context.get('request'),
            'exception_type': type(exc).__name__
        }
    )
    
    # Handle custom exceptions
    if isinstance(exc, CustomException):
        return APIResponse.error(
            message=exc.message,
            errors=exc.details,
            status_code=exc.status_code,
            error_code=exc.error_code
        )
    
    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        return APIResponse.validation_error(
            errors=exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
            message="Error de validación"
        )
    
    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        return APIResponse.error(
            message="Error de integridad en la base de datos",
            status_code=status.HTTP_409_CONFLICT,
            error_code="INTEGRITY_ERROR"
        )
    
    # Handle Http404
    if isinstance(exc, Http404):
        return APIResponse.not_found(
            message="Recurso no encontrado"
        )
    
    # Handle DRF exceptions
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': _get_error_message(exc),
            'error_code': _get_error_code(exc)
        }
        
        # Add detailed errors if available
        if hasattr(response, 'data') and response.data:
            if isinstance(response.data, dict):
                # Handle field-specific errors
                if 'detail' not in response.data:
                    custom_response_data['errors'] = response.data
                else:
                    custom_response_data['errors'] = response.data['detail']
            else:
                custom_response_data['errors'] = response.data
        
        response.data = custom_response_data
        return response
    
    # Handle unexpected exceptions
    logger.critical(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            'view': str(context.get('view', 'Unknown')),
            'request': context.get('request'),
            'exception_type': type(exc).__name__
        }
    )
    
    return APIResponse.server_error(
        message="Error interno del servidor",
        error_code="INTERNAL_SERVER_ERROR"
    )


def _get_error_message(exc) -> str:
    """Get appropriate error message for exception.
    
    Args:
        exc: Exception instance
        
    Returns:
        str: Error message
    """
    error_messages = {
        ValidationError: "Error de validación",
        AuthenticationFailed: "Error de autenticación",
        PermissionDenied: "Acceso prohibido",
        NotFound: "Recurso no encontrado",
        MethodNotAllowed: "Método no permitido",
        NotAcceptable: "Formato no aceptable",
        UnsupportedMediaType: "Tipo de media no soportado",
        Throttled: "Demasiadas solicitudes",
        ParseError: "Error al procesar la solicitud"
    }
    
    return error_messages.get(type(exc), "Error en la operación")


def _get_error_code(exc) -> str:
    """Get appropriate error code for exception.
    
    Args:
        exc: Exception instance
        
    Returns:
        str: Error code
    """
    error_codes = {
        ValidationError: "VALIDATION_ERROR",
        AuthenticationFailed: "AUTHENTICATION_FAILED",
        PermissionDenied: "PERMISSION_DENIED",
        NotFound: "NOT_FOUND",
        MethodNotAllowed: "METHOD_NOT_ALLOWED",
        NotAcceptable: "NOT_ACCEPTABLE",
        UnsupportedMediaType: "UNSUPPORTED_MEDIA_TYPE",
        Throttled: "THROTTLED",
        ParseError: "PARSE_ERROR"
    }
    
    return error_codes.get(type(exc), "UNKNOWN_ERROR")


class ExceptionMiddleware:
    """Middleware for handling exceptions at the Django level."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            logger.error(
                f"Middleware caught exception: {str(exc)}",
                exc_info=True,
                extra={
                    'request_path': request.path,
                    'request_method': request.method,
                    'user': getattr(request, 'user', None),
                    'exception_type': type(exc).__name__
                }
            )
            raise
    
    def process_exception(self, request, exception):
        """Process exceptions that occur during request processing.
        
        Args:
            request: Django request object
            exception: Exception instance
            
        Returns:
            HttpResponse or None
        """
        logger.error(
            f"Django exception: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': getattr(request, 'user', None),
                'exception_type': type(exception).__name__
            }
        )
        return None