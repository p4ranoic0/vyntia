import django_filters
from django.db import models
from apps.employees.models import Empleado

class EmpleadoFilter(django_filters.FilterSet):
    # Filtro para buscar por nombre (nombres, apellido paterno o materno)
    search = django_filters.CharFilter(method='filter_by_name', label='Buscar por nombre')
    
    # Filtro para buscar por DNI
    dni = django_filters.CharFilter(lookup_expr='icontains', label='Buscar por DNI')
    
    # Filtro por estado (activo/inactivo)
    estado = django_filters.BooleanFilter(label='Solo activos')
    
    def filter_by_name(self, queryset, name, value):
        """
        Filtro personalizado para buscar por nombres, apellido paterno o materno
        """
        if value:
            return queryset.filter(
                models.Q(nombres_empleado__icontains=value) |
                models.Q(apellido_paterno__icontains=value) |
                models.Q(apellido_materno__icontains=value)
            )
        return queryset
    
    class Meta:
        model = Empleado
        fields = ['search', 'dni', 'estado']