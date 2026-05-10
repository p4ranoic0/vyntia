"""Custom managers for identity models."""

from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone


class UsuarioManager(models.Manager):
    """Custom manager for User model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def get_by_natural_key(self, username):
        """Get user by username (natural key)."""
        return self.get(username=username)

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user."""
        if not username:
            raise ValueError("El username es obligatorio")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

    def activos(self):
        """Get active users (Django is_active AND estado_usuario='activo')."""
        return self.filter(is_active=True, estado_usuario="activo")

    def inactivos(self):
        """Get inactive users (is_active=False OR estado_usuario != 'activo')."""
        return self.filter(Q(is_active=False) | ~Q(estado_usuario="activo"))

    def con_roles(self):
        """Get users with their roles prefetched via the UserRole pivot."""
        return self.prefetch_related("roles_asignados__rol")

    def por_rol(self, nombre_rol: str):
        """Filter users with an active role assignment matching nombre_rol.

        Args:
            nombre_rol: Role name (case-insensitive substring match).

        Returns:
            QuerySet[User]
        """
        return self.filter(
            roles_asignados__rol__nombre_rol__icontains=nombre_rol,
            roles_asignados__estado_asignacion="activo",
        ).distinct()

    def login_reciente(self, dias: int = 30):
        """Get users with recent login.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Users with recent login
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_ult_login__gte=fecha_limite)

    def buscar(self, termino: str):
        """Search users by username or employee data.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching users
        """
        return self.filter(
            Q(nombres_usuario__icontains=termino)
            | Q(empleado__nombres_empleado__icontains=termino)
            | Q(empleado__apellido_paterno__icontains=termino)
            | Q(empleado__apellido_materno__icontains=termino)
        )
