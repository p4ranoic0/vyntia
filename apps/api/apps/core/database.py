"""Database utilities and routers for optimized database operations."""

import random
from django.conf import settings
from django.db import connections
from typing import Optional, Type, Any
from django.db.models import Model


class DatabaseRouter:
    """Database router for read/write splitting."""
    
    # Apps that should use the default database
    route_app_labels = {'app_rrhh', 'auth', 'contenttypes', 'sessions', 'admin'}
    
    def db_for_read(self, model: Type[Model], **hints) -> Optional[str]:
        """Suggest the database to read from.
        
        Args:
            model: Model class
            **hints: Additional hints
            
        Returns:
            str: Database alias or None
        """
        if model._meta.app_label in self.route_app_labels:
            # Use read replica if available in production
            if hasattr(settings, 'DATABASES') and 'read_replica' in settings.DATABASES:
                # Simple load balancing - could be enhanced with health checks
                return random.choice(['default', 'read_replica'])
            return 'default'
        return None
    
    def db_for_write(self, model: Type[Model], **hints) -> Optional[str]:
        """Suggest the database to write to.
        
        Args:
            model: Model class
            **hints: Additional hints
            
        Returns:
            str: Database alias or None
        """
        if model._meta.app_label in self.route_app_labels:
            # Always write to the default database
            return 'default'
        return None
    
    def allow_relation(self, obj1: Model, obj2: Model, **hints) -> Optional[bool]:
        """Allow relations if models are in the same app.
        
        Args:
            obj1: First model instance
            obj2: Second model instance
            **hints: Additional hints
            
        Returns:
            bool: Whether relation is allowed or None
        """
        db_set = {'default', 'read_replica'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db: str, app_label: str, model_name: Optional[str] = None, **hints) -> Optional[bool]:
        """Ensure that certain apps' models get created on the right database.
        
        Args:
            db: Database alias
            app_label: App label
            model_name: Model name
            **hints: Additional hints
            
        Returns:
            bool: Whether migration is allowed or None
        """
        if app_label in self.route_app_labels:
            # Only migrate on the default database
            return db == 'default'
        elif db == 'read_replica':
            # Don't migrate anything to read replica
            return False
        return None


class DatabaseHealthChecker:
    """Database health checker for monitoring connections."""
    
    @staticmethod
    def check_connection(db_alias: str = 'default') -> bool:
        """Check if database connection is healthy.
        
        Args:
            db_alias: Database alias to check
            
        Returns:
            bool: True if connection is healthy
        """
        try:
            connection = connections[db_alias]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    @staticmethod
    def check_all_connections() -> dict:
        """Check health of all configured database connections.
        
        Returns:
            dict: Database health status
        """
        health_status = {}
        for db_alias in settings.DATABASES.keys():
            health_status[db_alias] = DatabaseHealthChecker.check_connection(db_alias)
        return health_status
    
    @staticmethod
    def get_connection_info(db_alias: str = 'default') -> dict:
        """Get connection information for a database.
        
        Args:
            db_alias: Database alias
            
        Returns:
            dict: Connection information
        """
        try:
            connection = connections[db_alias]
            db_config = settings.DATABASES[db_alias]
            
            info = {
                'alias': db_alias,
                'engine': db_config.get('ENGINE'),
                'name': db_config.get('NAME'),
                'host': db_config.get('HOST'),
                'port': db_config.get('PORT'),
                'is_usable': connection.is_usable(),
                'queries_logged': len(connection.queries) if hasattr(connection, 'queries') else 0,
            }
            
            # Add connection pool info if available
            if hasattr(connection, 'pool'):
                info['pool_size'] = getattr(connection.pool, 'size', 'unknown')
                info['pool_checked_out'] = getattr(connection.pool, 'checkedout', 'unknown')
            
            return info
        except Exception as e:
            return {
                'alias': db_alias,
                'error': str(e),
                'is_usable': False
            }


class QueryOptimizer:
    """Utilities for query optimization."""
    
    @staticmethod
    def get_query_count() -> int:
        """Get total number of queries executed.
        
        Returns:
            int: Total query count
        """
        total_queries = 0
        for connection in connections.all():
            if hasattr(connection, 'queries'):
                total_queries += len(connection.queries)
        return total_queries
    
    @staticmethod
    def reset_query_count() -> None:
        """Reset query count for all connections."""
        for connection in connections.all():
            if hasattr(connection, 'queries'):
                connection.queries.clear()
    
    @staticmethod
    def get_slow_queries(threshold: float = 1.0) -> list:
        """Get queries that took longer than threshold.
        
        Args:
            threshold: Time threshold in seconds
            
        Returns:
            list: List of slow queries
        """
        slow_queries = []
        for connection in connections.all():
            if hasattr(connection, 'queries'):
                for query in connection.queries:
                    if float(query.get('time', 0)) > threshold:
                        slow_queries.append({
                            'sql': query['sql'],
                            'time': query['time'],
                            'connection': connection.alias
                        })
        return slow_queries
    
    @staticmethod
    def analyze_query_patterns() -> dict:
        """Analyze query patterns for optimization insights.
        
        Returns:
            dict: Query analysis results
        """
        analysis = {
            'total_queries': 0,
            'select_queries': 0,
            'insert_queries': 0,
            'update_queries': 0,
            'delete_queries': 0,
            'duplicate_queries': {},
            'tables_accessed': set(),
        }
        
        for connection in connections.all():
            if hasattr(connection, 'queries'):
                for query in connection.queries:
                    sql = query['sql'].strip().upper()
                    analysis['total_queries'] += 1
                    
                    # Count query types
                    if sql.startswith('SELECT'):
                        analysis['select_queries'] += 1
                    elif sql.startswith('INSERT'):
                        analysis['insert_queries'] += 1
                    elif sql.startswith('UPDATE'):
                        analysis['update_queries'] += 1
                    elif sql.startswith('DELETE'):
                        analysis['delete_queries'] += 1
                    
                    # Track duplicate queries
                    sql_normalized = ' '.join(sql.split())
                    if sql_normalized in analysis['duplicate_queries']:
                        analysis['duplicate_queries'][sql_normalized] += 1
                    else:
                        analysis['duplicate_queries'][sql_normalized] = 1
                    
                    # Extract table names (basic implementation)
                    if 'FROM' in sql:
                        parts = sql.split('FROM')[1].split()
                        if parts:
                            table_name = parts[0].strip('`"').split('.')[0]
                            analysis['tables_accessed'].add(table_name)
        
        # Convert set to list for JSON serialization
        analysis['tables_accessed'] = list(analysis['tables_accessed'])
        
        # Filter duplicate queries (only show duplicates)
        analysis['duplicate_queries'] = {
            sql: count for sql, count in analysis['duplicate_queries'].items() 
            if count > 1
        }
        
        return analysis


class TransactionManager:
    """Enhanced transaction management utilities."""
    
    @staticmethod
    def execute_in_transaction(func, *args, using='default', **kwargs):
        """Execute function within a database transaction.
        
        Args:
            func: Function to execute
            *args: Function arguments
            using: Database alias
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        from django.db import transaction
        
        with transaction.atomic(using=using):
            return func(*args, **kwargs)
    
    @staticmethod
    def bulk_create_optimized(model_class, objects, batch_size=1000, using='default'):
        """Optimized bulk create with batching.
        
        Args:
            model_class: Model class
            objects: List of model instances
            batch_size: Batch size for bulk operations
            using: Database alias
            
        Returns:
            list: Created objects
        """
        created_objects = []
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            created_batch = model_class.objects.using(using).bulk_create(
                batch, ignore_conflicts=False
            )
            created_objects.extend(created_batch)
        return created_objects
    
    @staticmethod
    def bulk_update_optimized(objects, fields, batch_size=1000, using='default'):
        """Optimized bulk update with batching.
        
        Args:
            objects: List of model instances to update
            fields: List of field names to update
            batch_size: Batch size for bulk operations
            using: Database alias
            
        Returns:
            int: Number of updated objects
        """
        from django.db import models
        
        if not objects:
            return 0
        
        model_class = objects[0].__class__
        total_updated = 0
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            updated_count = model_class.objects.using(using).bulk_update(
                batch, fields
            )
            total_updated += updated_count
        
        return total_updated