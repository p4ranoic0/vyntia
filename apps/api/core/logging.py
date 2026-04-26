"""Structured logging utilities for the application."""

import logging
import json
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: Formatted log message
        """
        # Base log data
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        extra_fields = getattr(record, '__dict__', {})
        excluded_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
            'filename', 'module', 'lineno', 'funcName', 'created',
            'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'getMessage', 'exc_info',
            'exc_text', 'stack_info'
        }
        
        for key, value in extra_fields.items():
            if key not in excluded_fields and not key.startswith('_'):
                log_data[key] = self._serialize_value(value)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON output.
        
        Args:
            value: Value to serialize
            
        Returns:
            Any: Serialized value
        """
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            return str(value)


class APILogger:
    """Logger for API operations."""
    
    def __init__(self, name: str = 'api'):
        self.logger = logging.getLogger(name)
    
    def log_request(self, request: HttpRequest, **kwargs) -> None:
        """Log API request.
        
        Args:
            request: Django request object
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'api_request',
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'content_type': request.content_type,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request)
        }
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            log_data['user_id'] = request.user.id
            log_data['username'] = request.user.username
        
        log_data.update(kwargs)
        self.logger.info("API request received", extra=log_data)
    
    def log_response(self, request: HttpRequest, response, duration: float = None, **kwargs) -> None:
        """Log API response.
        
        Args:
            request: Django request object
            response: Django response object
            duration: Request duration in seconds
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'api_response',
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_size': len(response.content) if hasattr(response, 'content') else 0
        }
        
        if duration is not None:
            log_data['duration'] = duration
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            log_data['user_id'] = request.user.id
            log_data['username'] = request.user.username
        
        log_data.update(kwargs)
        
        # Log level based on status code
        if response.status_code >= 500:
            self.logger.error("API response sent", extra=log_data)
        elif response.status_code >= 400:
            self.logger.warning("API response sent", extra=log_data)
        else:
            self.logger.info("API response sent", extra=log_data)
    
    def log_error(self, request: HttpRequest, error: Exception, **kwargs) -> None:
        """Log API error.
        
        Args:
            request: Django request object
            error: Exception that occurred
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'api_error',
            'method': request.method,
            'path': request.path,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            log_data['user_id'] = request.user.id
            log_data['username'] = request.user.username
        
        log_data.update(kwargs)
        self.logger.error("API error occurred", extra=log_data, exc_info=True)
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request.
        
        Args:
            request: Django request object
            
        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DatabaseLogger:
    """Logger for database operations."""
    
    def __init__(self, name: str = 'database'):
        self.logger = logging.getLogger(name)
    
    def log_query(self, query: str, params: Optional[tuple] = None, duration: float = None, **kwargs) -> None:
        """Log database query.
        
        Args:
            query: SQL query
            params: Query parameters
            duration: Query duration in seconds
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'database_query',
            'query': query,
            'params': params
        }
        
        if duration is not None:
            log_data['duration'] = duration
        
        log_data.update(kwargs)
        
        # Log slow queries as warnings
        if duration and duration > 1.0:
            self.logger.warning("Slow database query", extra=log_data)
        else:
            self.logger.debug("Database query executed", extra=log_data)
    
    def log_migration(self, migration_name: str, status: str, **kwargs) -> None:
        """Log database migration.
        
        Args:
            migration_name: Name of the migration
            status: Migration status (started, completed, failed)
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'database_migration',
            'migration_name': migration_name,
            'status': status
        }
        
        log_data.update(kwargs)
        
        if status == 'failed':
            self.logger.error("Database migration failed", extra=log_data)
        else:
            self.logger.info(f"Database migration {status}", extra=log_data)


class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self, name: str = 'security'):
        self.logger = logging.getLogger(name)
    
    def log_authentication(self, username: str, success: bool, ip_address: str, **kwargs) -> None:
        """Log authentication attempt.
        
        Args:
            username: Username attempting authentication
            success: Whether authentication was successful
            ip_address: Client IP address
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'authentication',
            'username': username,
            'success': success,
            'ip_address': ip_address
        }
        
        log_data.update(kwargs)
        
        if success:
            self.logger.info("User authenticated successfully", extra=log_data)
        else:
            self.logger.warning("Authentication failed", extra=log_data)
    
    def log_authorization(self, user_id: int, resource: str, action: str, success: bool, **kwargs) -> None:
        """Log authorization attempt.
        
        Args:
            user_id: User ID
            resource: Resource being accessed
            action: Action being performed
            success: Whether authorization was successful
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'authorization',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'success': success
        }
        
        log_data.update(kwargs)
        
        if success:
            self.logger.info("User authorized successfully", extra=log_data)
        else:
            self.logger.warning("Authorization failed", extra=log_data)
    
    def log_suspicious_activity(self, description: str, ip_address: str, user_id: Optional[int] = None, **kwargs) -> None:
        """Log suspicious activity.
        
        Args:
            description: Description of suspicious activity
            ip_address: Client IP address
            user_id: User ID if known
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'suspicious_activity',
            'description': description,
            'ip_address': ip_address
        }
        
        if user_id:
            log_data['user_id'] = user_id
        
        log_data.update(kwargs)
        self.logger.warning("Suspicious activity detected", extra=log_data)


class BusinessLogger:
    """Logger for business operations."""
    
    def __init__(self, name: str = 'business'):
        self.logger = logging.getLogger(name)
    
    def log_employee_action(self, action: str, employee_id: int, performed_by: int, **kwargs) -> None:
        """Log employee-related action.
        
        Args:
            action: Action performed (created, updated, deleted)
            employee_id: Employee ID
            performed_by: User ID who performed the action
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'employee_action',
            'action': action,
            'employee_id': employee_id,
            'performed_by': performed_by
        }
        
        log_data.update(kwargs)
        self.logger.info(f"Employee {action}", extra=log_data)
    
    def log_payroll_action(self, action: str, payroll_id: int, employee_id: int, performed_by: int, **kwargs) -> None:
        """Log payroll-related action.
        
        Args:
            action: Action performed
            payroll_id: Payroll ID
            employee_id: Employee ID
            performed_by: User ID who performed the action
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'payroll_action',
            'action': action,
            'payroll_id': payroll_id,
            'employee_id': employee_id,
            'performed_by': performed_by
        }
        
        log_data.update(kwargs)
        self.logger.info(f"Payroll {action}", extra=log_data)
    
    def log_role_change(self, user_id: int, old_roles: list, new_roles: list, performed_by: int, **kwargs) -> None:
        """Log role change.
        
        Args:
            user_id: User ID whose roles changed
            old_roles: Previous roles
            new_roles: New roles
            performed_by: User ID who performed the change
            **kwargs: Additional log data
        """
        log_data = {
            'event_type': 'role_change',
            'user_id': user_id,
            'old_roles': old_roles,
            'new_roles': new_roles,
            'performed_by': performed_by
        }
        
        log_data.update(kwargs)
        self.logger.info("User roles changed", extra=log_data)


# Logger instances
api_logger = APILogger()
database_logger = DatabaseLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def setup_logging() -> None:
    """Setup logging configuration."""
    # Configure root logger
    logging.basicConfig(
        level=getattr(settings, 'LOG_LEVEL', logging.INFO),
        format='%(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(getattr(settings, 'LOG_FILE', 'app.log'))
        ]
    )
    
    # Set formatter for all handlers
    formatter = StructuredFormatter()
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)