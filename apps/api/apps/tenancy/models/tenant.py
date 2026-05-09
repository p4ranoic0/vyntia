"""Tenant model — the SaaS subscriber entity.

A Tenant represents one paying customer of VYNTIA. It owns the subdomain
(`<slug>.vyntia.pe`), plan tier, lifecycle status, and trial window. All
tenant-scoped business data (employees, contracts, payroll, etc.) FKs to
this entity in C.1.
"""

import uuid

from django.db import models


PLAN_CHOICES = [
    ("starter", "Starter"),
    ("pro", "Pro"),
    ("enterprise", "Enterprise"),
    ("govtech", "GovTech"),
]

STATUS_CHOICES = [
    ("trial", "Trial"),
    ("active", "Active"),
    ("suspended", "Suspended"),
    ("cancelled", "Cancelled"),
]


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=63, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    ruc = models.CharField(max_length=11)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    max_users = models.IntegerField(default=10)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="tenants_created",
    )

    class Meta:
        db_table = "tenancy_tenant"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "plan"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.slug})"
