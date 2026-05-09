"""Modelo para configuración de datos de la empresa/institución."""
from django.db import models


class Company(models.Model):
    """Configuración de datos institucionales (per-tenant during C.x migration)."""

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )

    nombre = models.CharField(max_length=300, default='Institución Pública', help_text='Nombre de la institución')
    ruc = models.CharField(max_length=20, default='20000000000', help_text='RUC de la institución')
    direccion = models.CharField(max_length=300, default='', help_text='Dirección de la institución')
    distrito = models.CharField(max_length=100, default='', blank=True)
    provincia = models.CharField(max_length=100, default='Lima', blank=True)
    departamento = models.CharField(max_length=100, default='Lima', blank=True)
    telefono = models.CharField(max_length=50, default='', blank=True)
    email = models.EmailField(max_length=150, default='', blank=True)
    web = models.URLField(max_length=200, default='', blank=True)
    logo = models.ImageField(upload_to='empresa/', null=True, blank=True, help_text='Logo institucional')
    representante_legal = models.CharField(max_length=200, default='', blank=True, help_text='Nombre del representante legal')
    cargo_representante = models.CharField(max_length=200, default='', blank=True, help_text='Cargo del representante')
    dni_representante = models.CharField(max_length=20, default='', blank=True, help_text='DNI del representante')
    resolucion_creacion = models.CharField(max_length=200, default='', blank=True, help_text='Resolución de creación')

    class Meta:
        db_table = 'configuracion_empresa'
        verbose_name = 'Configuración de Empresa'
        constraints = [
            models.UniqueConstraint(
                fields=["tenant"],
                condition=models.Q(tenant__isnull=False),
                name="unique_company_per_tenant",
            ),
        ]

    def __str__(self):
        return self.nombre

    @classmethod
    def get_config(cls, tenant=None):
        """Returns the Company config for the given tenant.

        Backward-compat: if tenant is None, falls back to the legacy singleton
        (pk=1). This fallback will be removed in C.3 once middleware ensures
        every authenticated request has a tenant context.
        """
        if tenant is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            return obj
        return cls.objects.filter(tenant=tenant).first()
