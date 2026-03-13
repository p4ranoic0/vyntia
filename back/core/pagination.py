"""Custom pagination classes for API endpoints."""

from typing import Dict, Any, Optional
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import InvalidPage
from django.http import Http404
from .responses import APIResponse


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class with unified response format."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data: list) -> Response:
        """Return a paginated style Response object.
        
        Args:
            data: Serialized data for the current page
            
        Returns:
            Response: Unified API response with pagination metadata
        """
        meta = {
            "pagination": {
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page": self.page.previous_page_number() if self.page.has_previous() else None,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link()
                }
            }
        }
        
        return APIResponse.success(
            data=data,
            message="Datos obtenidos exitosamente",
            meta=meta
        )
    
    def paginate_queryset(self, queryset, request, view=None):
        """Paginate a queryset if required.
        
        Args:
            queryset: The queryset to paginate
            request: The request object
            view: The view object (optional)
            
        Returns:
            Page object or None if pagination is not required
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None
            
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise Http404(msg)
            
        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
            
        self.request = request
        return list(self.page)


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination class for large datasets."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'
    
    def get_paginated_response(self, data: list) -> Response:
        """Return a paginated style Response object for large datasets.
        
        Args:
            data: Serialized data for the current page
            
        Returns:
            Response: Unified API response with pagination metadata
        """
        meta = {
            "pagination": {
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page": self.page.previous_page_number() if self.page.has_previous() else None,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link()
                }
            }
        }
        
        return APIResponse.success(
            data=data,
            message="Datos obtenidos exitosamente",
            meta=meta
        )


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination class for small datasets."""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data: list) -> Response:
        """Return a paginated style Response object for small datasets.
        
        Args:
            data: Serialized data for the current page
            
        Returns:
            Response: Unified API response with pagination metadata
        """
        meta = {
            "pagination": {
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page": self.page.previous_page_number() if self.page.has_previous() else None,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link()
                }
            }
        }
        
        return APIResponse.success(
            data=data,
            message="Datos obtenidos exitosamente",
            meta=meta
        )


class NoPagination:
    """No pagination class for endpoints that should return all results."""
    
    def paginate_queryset(self, queryset, request, view=None):
        """Return None to indicate no pagination."""
        return None
    
    def get_paginated_response(self, data: list) -> Response:
        """Return a non-paginated response.
        
        Args:
            data: Serialized data
            
        Returns:
            Response: Unified API response without pagination
        """
        return APIResponse.success(
            data=data,
            message="Datos obtenidos exitosamente"
        )


class CustomPagination:
    """Utility class for custom pagination logic."""
    
    @staticmethod
    def get_pagination_class(view_name: str, default_class=StandardResultsSetPagination):
        """Get appropriate pagination class based on view name.
        
        Args:
            view_name: Name of the view
            default_class: Default pagination class
            
        Returns:
            Pagination class
        """
        pagination_mapping = {
            'empleado': LargeResultsSetPagination,
            'boleta': LargeResultsSetPagination,
            'area': SmallResultsSetPagination,
            'rol': SmallResultsSetPagination,
            'permiso': SmallResultsSetPagination,
        }
        
        return pagination_mapping.get(view_name.lower(), default_class)
    
    @staticmethod
    def paginate_queryset(
        queryset,
        request,
        page_size: Optional[int] = None,
        pagination_class=StandardResultsSetPagination
    ):
        """Manually paginate a queryset.
        
        Args:
            queryset: QuerySet to paginate
            request: Request object
            page_size: Custom page size
            pagination_class: Pagination class to use
            
        Returns:
            Tuple of (paginated_data, pagination_response)
        """
        paginator = pagination_class()
        
        if page_size:
            paginator.page_size = page_size
            
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        if paginated_queryset is not None:
            return paginated_queryset, paginator
        
        return queryset, None