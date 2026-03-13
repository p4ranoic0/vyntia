"""Custom middleware for the application."""

import json
import logging
import time
from typing import Callable, Optional

from app_rrhh.models import Usuario
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging API requests and responses."""

    def process_request(self, request: HttpRequest) -> None:
        """Log incoming request details.

        Args:
            request: Django request object
        """
        request.start_time = time.time()

        # Skip logging for certain paths
        skip_paths = ["/admin/", "/static/", "/media/", "/favicon.ico"]
        if any(request.path.startswith(path) for path in skip_paths):
            return

        # Log request details
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "user": str(request.user) if hasattr(request, "user") else "Anonymous",
                "ip_address": self._get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "query_params": dict(request.GET),
                "content_type": request.content_type,
            },
        )

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Log response details.

        Args:
            request: Django request object
            response: Django response object

        Returns:
            HttpResponse: The response object
        """
        # Skip logging for certain paths
        skip_paths = ["/admin/", "/static/", "/media/", "/favicon.ico"]
        if any(request.path.startswith(path) for path in skip_paths):
            return response

        # Calculate request duration
        duration = None
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time

        # Log response details
        logger.info(
            f"Request completed: {request.method} {request.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration": duration,
                "user": str(request.user) if hasattr(request, "user") else "Anonymous",
                "ip_address": self._get_client_ip(request),
                "response_size": (
                    len(response.content) if hasattr(response, "content") else 0
                ),
            },
        )

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request.

        Args:
            request: Django request object

        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware for monitoring API performance."""

    def process_request(self, request: HttpRequest) -> None:
        """Start performance monitoring.

        Args:
            request: Django request object
        """
        request.start_time = time.time()
        request.db_queries_start = len(getattr(settings, "DEBUG_TOOLBAR_PANELS", []))

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Log performance metrics.

        Args:
            request: Django request object
            response: Django response object

        Returns:
            HttpResponse: The response object
        """
        if not hasattr(request, "start_time"):
            return response

        duration = time.time() - request.start_time

        # Log slow requests
        if duration > 1.0:  # Requests taking more than 1 second
            logger.warning(
                f"Slow request detected: {request.method} {request.path} took {duration:.2f}s",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "duration": duration,
                    "status_code": response.status_code,
                    "user": (
                        str(request.user) if hasattr(request, "user") else "Anonymous"
                    ),
                },
            )

        # Add performance headers
        response["X-Response-Time"] = f"{duration:.3f}s"

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware for adding security headers."""

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Add security headers to response.

        Args:
            request: Django request object
            response: Django response object

        Returns:
            HttpResponse: The response object with security headers
        """
        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        # Allow same-origin iframes for /media/ paths (PDF preview in DocumentViewer)
        if request.path.startswith("/media/"):
            response["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add CSP header for API endpoints
        if request.path.startswith("/api/"):
            response["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none';"
            )

        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.rate_limit = getattr(
            settings, "API_RATE_LIMIT", 100
        )  # requests per minute
        self.rate_limit_window = 60  # seconds

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request with rate limiting.

        Args:
            request: Django request object

        Returns:
            HttpResponse: The response object
        """
        # Skip rate limiting for certain paths
        skip_paths = ["/admin/", "/static/", "/media/"]
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        # Get client identifier
        client_id = self._get_client_identifier(request)

        # Check rate limit
        if self._is_rate_limited(client_id):
            logger.warning(
                f"Rate limit exceeded for {client_id}",
                extra={
                    "client_id": client_id,
                    "path": request.path,
                    "method": request.method,
                },
            )

            response = HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "message": "Rate limit exceeded",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                    }
                ),
                status=429,
                content_type="application/json",
            )
            response["Retry-After"] = str(self.rate_limit_window)
            return response

        return self.get_response(request)

    def _get_client_identifier(self, request: HttpRequest) -> str:
        """Get unique identifier for client.

        Args:
            request: Django request object

        Returns:
            str: Client identifier
        """
        # Use user ID if authenticated, otherwise use IP
        if hasattr(request, "user") and not isinstance(request.user, AnonymousUser):
            return f"user_{request.user.id}"
        else:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[
                0
            ] or request.META.get("REMOTE_ADDR")
            return f"ip_{ip}"

    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit.

        Args:
            client_id: Client identifier

        Returns:
            bool: True if rate limited
        """
        cache_key = f"rate_limit_{client_id}"
        current_requests = cache.get(cache_key, 0)

        if current_requests >= self.rate_limit:
            return True

        # Increment counter
        cache.set(cache_key, current_requests + 1, self.rate_limit_window)
        return False


class AuditMiddleware(MiddlewareMixin):
    """Middleware for auditing user actions."""

    def process_request(self, request: HttpRequest) -> None:
        """Log user actions for audit purposes.

        Args:
            request: Django request object
        """
        # Skip auditing for certain paths and methods
        skip_paths = ["/admin/", "/static/", "/media/", "/api/v1/auth/token/refresh/"]
        if any(request.path.startswith(path) for path in skip_paths):
            return

        if request.method in ["GET", "OPTIONS", "HEAD"]:
            return

        # Log user actions
        if hasattr(request, "user") and not isinstance(request.user, AnonymousUser):
            try:
                # Get request body for audit
                body = None
                if (
                    hasattr(request, "body")
                    and request.content_type == "application/json"
                ):
                    try:
                        body = json.loads(request.body.decode("utf-8"))
                        # Remove sensitive fields
                        if isinstance(body, dict):
                            sensitive_fields = ["password", "token", "secret"]
                            for field in sensitive_fields:
                                if field in body:
                                    body[field] = "***REDACTED***"
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = None

                logger.info(
                    f"User action: {request.user} performed {request.method} on {request.path}",
                    extra={
                        "user_id": request.user.id,
                        "username": request.user.username,
                        "action": request.method,
                        "resource": request.path,
                        "ip_address": self._get_client_ip(request),
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                        "request_data": body,
                        "timestamp": time.time(),
                    },
                )
            except Exception as e:
                logger.error(f"Error in audit middleware: {str(e)}")

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request.

        Args:
            request: Django request object

        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CORSMiddleware(MiddlewareMixin):
    """Custom CORS middleware for fine-grained control."""

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Add CORS headers to response.

        Args:
            request: Django request object
            response: Django response object

        Returns:
            HttpResponse: The response object with CORS headers
        """
        # Get allowed origins from settings
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        origin = request.META.get("HTTP_ORIGIN")

        if origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response["Access-Control-Allow-Headers"] = (
                "Accept, Authorization, Content-Type, X-CSRFToken"
            )
            response["Access-Control-Max-Age"] = "86400"

        return response


class HealthCheckMiddleware(MiddlewareMixin):
    """Middleware for health check endpoints."""

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Handle health check requests.

        Args:
            request: Django request object

        Returns:
            HttpResponse or None: Health check response if applicable
        """
        if request.path == "/health/":
            return HttpResponse(
                json.dumps(
                    {
                        "status": "healthy",
                        "timestamp": time.time(),
                        "version": getattr(settings, "APP_VERSION", "1.0.0"),
                    }
                ),
                content_type="application/json",
            )

        return None


class JWTCookieMiddleware(MiddlewareMixin):
    """Middleware to extract JWT tokens from cookies and set them in Authorization header."""

    def process_request(self, request: HttpRequest) -> None:
        """Extract JWT token from cookies and set in Authorization header.

        Args:
            request: Django request object
        """
        # Skip for certain paths
        skip_paths = ["/admin/", "/static/", "/media/", "/favicon.ico", "/health/"]
        if any(request.path.startswith(path) for path in skip_paths):
            return

        # Debug: Log cookies and path
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"JWTCookieMiddleware: Path: {request.path}")
        logger.info(f"JWTCookieMiddleware: Cookies: {list(request.COOKIES.keys())}")

        # Get access token from cookies
        access_token = request.COOKIES.get("access_token")

        if access_token:
            # Set the Authorization header for DRF JWT authentication
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            logger.info(
                f"JWTCookieMiddleware: Token configurado en Authorization header"
            )
        else:
            logger.warning(
                f"JWTCookieMiddleware: No se encontro access_token en cookies"
            )

        return None
