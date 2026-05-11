"""Position — catalog of job positions with inline versioning (ADR-B.7).

Position is the master catalog of "what jobs exist in this org" — distinct
from Plaza ("which positions are currently occupied / vacant / frozen").

Versioning (ADR-B.7):
- Each Position row is immutable for the set of "versioned" fields (name,
  department, occupational_category, ciuo_code, reports_to). Changing those
  requires `create_new_version()` which makes a new row, links via
  `parent_version`, and flips the previous row's `is_current` to False.
- Non-versioned fields (typos, internal notes) update in place.
- Active references (Plaza, EmploymentData) point at the specific version
  they were issued against.
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Position(models.Model):
    """Catalog position — versioned per ADR-B.7."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    # Identity
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)

    # Versioning (ADR-B.7)
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='successors',
    )
    effective_date = models.DateField(default=timezone.now)
    is_current = models.BooleanField(default=True, db_index=True)

    # Classification
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.PROTECT,
        related_name='positions',
    )
    occupational_category = models.ForeignKey(
        'organization.OccupationalCategory',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    ciuo_code = models.ForeignKey(
        'organization.CIUOCode',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # Reporting line (within position graph; Employee reporting flows via Plaza)
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='direct_reports',
    )

    # Ley 30709 category (B.7) — nullable while CCF rolls out per tenant.
    category = models.ForeignKey(
        'compensation.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='positions',
        help_text='Ley 30709 category from CCF (post-B.7). Nullable while CCF rolls out.',
    )

    # SERVIR / Ley 30057 classification (B.8). Nullable — only populated on
    # public-sector tenants. Private tenants leave these blank.
    SERVIR_GROUP_CHOICES = [
        ('fp', 'Funcionario Público'),
        ('dp', 'Directivo Público'),
        ('cc', 'Servidor Civil de Carrera'),
        ('cs', 'Servidor de Actividades Complementarias'),
        ('cf', 'Servidor de Confianza'),
    ]
    SERVIR_LEVEL_CHOICES = [
        ('cf_1', 'CF-1 (Inicial)'),
        ('cf_2', 'CF-2 (Intermedio)'),
        ('cf_3', 'CF-3 (Avanzado)'),
        ('cf_4', 'CF-4 (Senior)'),
        ('dp_1', 'DP-1'),
        ('dp_2', 'DP-2'),
        ('dp_3', 'DP-3'),
        ('dp_4', 'DP-4'),
    ]
    SALARY_TIER_CHOICES = [
        ('principal', 'Principal'),
        ('ajustada', 'Ajustada'),
        ('priorizada', 'Priorizada'),
    ]

    servir_group = models.CharField(
        max_length=10,
        choices=SERVIR_GROUP_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text='Ley 30057 grupo de servidor civil. Solo para tenants sector público.',
    )
    servir_level = models.CharField(
        max_length=10,
        choices=SERVIR_LEVEL_CHOICES,
        null=True,
        blank=True,
        help_text='Nivel SERVIR para servidor de carrera o directivo público.',
    )
    salary_tier = models.CharField(
        max_length=20,
        choices=SALARY_TIER_CHOICES,
        null=True,
        blank=True,
        help_text='D.S. 138-2014-EF compensación principal / ajustada / priorizada.',
    )
    familia_puesto = models.CharField(
        max_length=100,
        blank=True,
        help_text='SERVIR familia de puestos (agrupación temática).',
    )

    # Lifecycle
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='positions_created',
    )

    class Meta:
        db_table = 'position'
        ordering = ['code', '-version']
        indexes = [
            models.Index(fields=['tenant', 'code']),
            models.Index(fields=['tenant', 'is_current']),
            models.Index(fields=['department']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code', 'version'],
                name='unique_position_code_version_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.code} v{self.version} - {self.name}"

    # Versioned vs non-versioned fields per ADR-B.7
    VERSIONED_FIELDS = (
        'name',
        'department',
        'occupational_category',
        'ciuo_code',
        'reports_to',
    )

    @transaction.atomic
    def create_new_version(self, *, effective_date=None, **changes):
        """Create the next version of this Position.

        Args:
            effective_date: When the new version takes effect. Defaults to today.
            **changes: Field overrides for the new version. Only fields in
                       VERSIONED_FIELDS warrant a new version; passing other
                       fields will still apply them but the audit semantics
                       are unchanged.

        Returns:
            The new Position row (`is_current=True`); the previous row has
            `is_current=False`.
        """
        if not self.is_current:
            raise ValidationError(
                "Solo se puede versionar la versión vigente "
                f"(esta Position v{self.version} ya fue superada)."
            )

        new = Position(
            tenant=self.tenant,
            code=self.code,
            name=self.name,
            version=self.version + 1,
            parent_version=self,
            effective_date=effective_date or timezone.now().date(),
            is_current=True,
            department=self.department,
            occupational_category=self.occupational_category,
            ciuo_code=self.ciuo_code,
            reports_to=self.reports_to,
            is_active=True,
            description=self.description,
            created_by=changes.pop('created_by', None) or self.created_by,
        )
        for k, v in changes.items():
            setattr(new, k, v)

        # Flip current; save new — both atomically
        self.is_current = False
        self.save(update_fields=['is_current'])
        new.save()
        return new

    @property
    def has_successors(self):
        """Has this Position been superseded by a newer version?"""
        return self.successors.exists()
