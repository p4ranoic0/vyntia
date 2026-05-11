"""Candidate — external person participating in selection processes (B.9).

Decoupled from `identity.User`. Most candidates never receive a system
account; the few who are hired link via `Employee.candidate_id` (post-B.10
Vinculación). Storing candidates as their own model also enables a single
person to apply to multiple JobPostings under the same tenant without
re-entering identity data.
"""
import uuid

from django.db import models


class Candidate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'No binario / sin declarar'),
    ]
    DOC_TYPE_CHOICES = [
        ('dni', 'DNI'),
        ('ce', 'Carné de Extranjería'),
        ('passport', 'Pasaporte'),
        ('ptp', 'PTP'),
    ]

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
    document_type = models.CharField(
        max_length=10, choices=DOC_TYPE_CHOICES, default='dni',
    )
    document_number = models.CharField(max_length=20, db_index=True)
    first_names = models.CharField(max_length=100)
    last_names = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)

    # Career snapshot — denormalized to power filtering and ranking without
    # joining/extracting from CV. Full document lives in cv_file.
    years_experience = models.PositiveIntegerField(default=0)
    highest_education = models.CharField(max_length=100, blank=True)

    cv_file = models.FileField(
        upload_to='candidates/%Y/%m/', null=True, blank=True,
    )

    source = models.CharField(
        max_length=50,
        blank=True,
        help_text=(
            'Acquisition channel: internal_referral | website | linkedin | '
            'servir | walk_in | other.'
        ),
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'document_number']),
            models.Index(fields=['tenant', 'email']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'document_type', 'document_number'],
                name='unique_candidate_doc_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.document_type.upper()} {self.document_number})"

    @property
    def full_name(self):
        return f"{self.first_names} {self.last_names}".strip()
