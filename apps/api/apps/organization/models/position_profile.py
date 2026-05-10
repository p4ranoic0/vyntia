"""PositionProfile, PositionFunction, PositionRequirement — Job Description models."""
import uuid

from django.db import models


class PositionProfile(models.Model):
    """1-to-1 profile / job description for a Position.

    Per Maestro Module 02 § 2.2: contains mission, work conditions, KPI list,
    and tag-style competency lists (JSON). Functions and requirements are
    list-shape and live in their own models (PositionFunction,
    PositionRequirement) for queryability and ordering.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.OneToOneField(
        'organization.Position',
        on_delete=models.CASCADE,
        related_name='profile',
    )

    mission = models.TextField(blank=True)
    technical_competencies = models.JSONField(default=list, blank=True)
    soft_competencies = models.JSONField(default=list, blank=True)
    work_conditions = models.TextField(blank=True)
    kpis = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position_profile'

    def __str__(self):
        return f"Profile for {self.position}"


class PositionFunction(models.Model):
    """One function entry on a Position's profile. Ordered + primary/secondary."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.CASCADE,
        related_name='functions',
    )
    description = models.TextField()
    is_primary = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position_function'
        ordering = ['order', 'id']

    def __str__(self):
        desc_preview = self.description[:60]
        return f"{self.position.code}: {desc_preview}"


class PositionRequirement(models.Model):
    """One requirement entry on a Position (education, experience, etc.)."""

    KIND_CHOICES = [
        ('education', 'Educación'),
        ('experience', 'Experiencia'),
        ('language', 'Idioma'),
        ('certification', 'Certificación'),
        ('other', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.CASCADE,
        related_name='requirements',
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    description = models.CharField(max_length=300)
    is_required = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position_requirement'
        ordering = ['kind', 'id']
        indexes = [
            models.Index(fields=['position', 'kind']),
        ]

    def __str__(self):
        return f"{self.position.code}: {self.get_kind_display()} - {self.description}"
