# -*- coding: utf-8 -*-
"""
Manager personalizado para el modelo Usuario

Contiene métodos de consulta optimizados y funcionalidades específicas
para el modelo Usuario.
"""

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from datetime import timedelta


class UsuarioManager(BaseUserManager):
    """Custom manager for Usuario model."""
    
    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related('empleado')
    
    def get_by_natural_key(self, username):
        """Get user by username (natural key)."""
        return self.get(username=username)
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user."""
        if not username:
            raise ValueError('El username es obligatorio')
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def activos(self):
        """Return active users."""
        return self.filter(is_active=True)
    
    def inactivos(self):
        """Return inactive users."""
        return self.filter(is_active=False)
    
    def con_roles(self):
        """Return users with roles."""
        return self.filter(usuario_roles__isnull=False).distinct()
    
    def por_rol(self, rol_nombre):
        """Return users by role name."""
        return self.filter(usuario_roles__rol__nombre=rol_nombre)
    
    def login_reciente(self, dias=30):
        """Return users with recent login."""
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(last_login__gte=fecha_limite)
    
    def buscar(self, termino):
        """Search users by username, email, or names."""
        return self.filter(
            Q(username__icontains=termino) |
            Q(email__icontains=termino) |
            Q(nombres_usuario__icontains=termino) |
            Q(apellidos_usuario__icontains=termino)
        )