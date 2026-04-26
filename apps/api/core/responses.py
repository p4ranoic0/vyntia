"""Unified response structures for API endpoints."""

from typing import Any, Dict, List, Optional, Union
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import QuerySet


class APIResponse:
    """Unified API response structure."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operación exitosa",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Create a successful response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response_data["meta"] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "Error en la operación",
        errors: Optional[Union[Dict[str, List[str]], List[str], str]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None
    ) -> Response:
        """Create an error response.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": False,
            "message": message
        }
        
        if errors:
            response_data["errors"] = errors
            
        if error_code:
            response_data["error_code"] = error_code
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated(
        queryset: QuerySet,
        page: int,
        page_size: int,
        serializer_class,
        context: Optional[Dict[str, Any]] = None,
        message: str = "Datos obtenidos exitosamente"
    ) -> Response:
        """Create a paginated response.
        
        Args:
            queryset: Django QuerySet to paginate
            page: Page number
            page_size: Items per page
            serializer_class: Serializer class for data
            context: Serializer context
            message: Success message
            
        Returns:
            Response: DRF Response object with pagination
        """
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = serializer_class(
            page_obj.object_list,
            many=True,
            context=context or {}
        )
        
        meta = {
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_size": page_size,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None
            }
        }
        
        return APIResponse.success(
            data=serializer.data,
            message=message,
            meta=meta
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Recurso creado exitosamente"
    ) -> Response:
        """Create a 201 Created response.
        
        Args:
            data: Created resource data
            message: Success message
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "Recurso actualizado exitosamente"
    ) -> Response:
        """Create an update response.
        
        Args:
            data: Updated resource data
            message: Success message
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.success(
            data=data,
            message=message
        )
    
    @staticmethod
    def deleted(
        message: str = "Recurso eliminado exitosamente"
    ) -> Response:
        """Create a delete response.
        
        Args:
            message: Success message
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.success(
            message=message,
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def not_found(
        message: str = "Recurso no encontrado",
        error_code: str = "RESOURCE_NOT_FOUND"
    ) -> Response:
        """Create a 404 Not Found response.
        
        Args:
            message: Error message
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code
        )
    
    @staticmethod
    def unauthorized(
        message: str = "No autorizado",
        error_code: str = "UNAUTHORIZED"
    ) -> Response:
        """Create a 401 Unauthorized response.
        
        Args:
            message: Error message
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code
        )
    
    @staticmethod
    def forbidden(
        message: str = "Acceso prohibido",
        error_code: str = "FORBIDDEN"
    ) -> Response:
        """Create a 403 Forbidden response.
        
        Args:
            message: Error message
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code
        )
    
    @staticmethod
    def validation_error(
        errors: Union[Dict[str, List[str]], List[str], str],
        message: str = "Error de validación",
        error_code: str = "VALIDATION_ERROR"
    ) -> Response:
        """Create a 422 Validation Error response.
        
        Args:
            errors: Validation errors
            message: Error message
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code
        )
    
    @staticmethod
    def server_error(
        message: str = "Error interno del servidor",
        error_code: str = "INTERNAL_SERVER_ERROR"
    ) -> Response:
        """Create a 500 Internal Server Error response.
        
        Args:
            message: Error message
            error_code: Specific error code
            
        Returns:
            Response: DRF Response object
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code
        )