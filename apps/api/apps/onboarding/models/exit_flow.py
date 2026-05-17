"""ExitInterview + HandoverChecklist + HandoverItem + SystemsOffboarding (B.14).

Coordinación operativa del cese:
- ExitInterview: entrevista de salida (6 preguntas estándar + sentiment).
- HandoverChecklist: entrega de cargo formal (firmada por saliente + entrante).
- HandoverItem: cada elemento a entregar (proyecto / documento / equipo / acceso).
- SystemsOffboarding: revocación de accesos a sistemas (correo / VPN / ERP / AD / etc.).

Las 3 entidades son OneToOne con Termination y se scaffoldean juntas al
inicio del cese vía exit_flow_service.scaffold_exit_flow.

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #126.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ExitInterview(models.Model):
    SENTIMENTS = [
        ('positivo', 'Positivo'),
        ('neutral', 'Neutral'),
        ('negativo', 'Negativo'),
        ('mixto', 'Mixto'),
        ('no_responde', 'No responde'),
    ]
    STATUSES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('skipped', 'Omitida'),
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

    termination = models.OneToOneField(
        'contracts.Termination',
        on_delete=models.CASCADE,
        related_name='exit_interview',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='pending', db_index=True,
    )
    answers = models.JSONField(
        default=dict, blank=True,
        help_text='Mapa pregunta_id → respuesta (6 preguntas estándar por defecto)',
    )
    sentiment = models.CharField(
        max_length=15, choices=SENTIMENTS, blank=True,
    )
    comments = models.TextField(blank=True)
    interviewer = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    interview_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exit_interview'
        ordering = ['-created_at']

    def __str__(self):
        return f'Exit interview {self.termination_id} ({self.status})'

    def mark_completed(self, *, answers, sentiment, comments='', interviewer=None, interview_date=None):
        if not answers:
            raise ValidationError('answers payload is required')
        self.status = 'completed'
        self.answers = answers
        self.sentiment = sentiment
        if comments:
            self.comments = comments
        if interviewer:
            self.interviewer = interviewer
        self.interview_date = interview_date or timezone.now().date()
        self.save()

    def mark_skipped(self, *, reason=''):
        self.status = 'skipped'
        if reason:
            self.comments = reason
        self.save(update_fields=['status', 'comments', 'updated_at'])


class HandoverChecklist(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En entrega'),
        ('completed', 'Entrega completada'),
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

    termination = models.OneToOneField(
        'contracts.Termination',
        on_delete=models.CASCADE,
        related_name='handover_checklist',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='draft', db_index=True,
    )
    receiving_user = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text='Trabajador entrante que recibe el cargo',
    )

    signed_by_outgoing_at = models.DateTimeField(null=True, blank=True)
    signed_by_incoming_at = models.DateTimeField(null=True, blank=True)
    signed_by_outgoing = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    signed_by_incoming = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'handover_checklist'
        ordering = ['-created_at']

    def __str__(self):
        return f'Handover {self.termination_id} ({self.status})'

    def mark_completed(self, *, signed_by_outgoing, signed_by_incoming):
        # Todos los items requeridos deben estar entregados o no_aplica.
        pendientes = self.items.filter(
            is_required=True, status='pendiente',
        ).count()
        if pendientes:
            raise ValidationError(
                f'{pendientes} items requeridos siguen pendientes; '
                'márcalos como entregado o no_aplica antes de completar'
            )
        now = timezone.now()
        self.signed_by_outgoing = signed_by_outgoing
        self.signed_by_outgoing_at = now
        self.signed_by_incoming = signed_by_incoming
        self.signed_by_incoming_at = now
        self.status = 'completed'
        self.completed_at = now
        self.save()


class HandoverItem(models.Model):
    KINDS = [
        ('proyecto', 'Proyecto en curso'),
        ('documento', 'Documento / archivo'),
        ('equipo', 'Equipo / activo físico'),
        ('acceso', 'Acceso / credencial'),
        ('credencial', 'Credencial / contraseña'),
        ('otro', 'Otro'),
    ]
    STATUSES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
        ('no_aplica', 'No aplica'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checklist = models.ForeignKey(
        'onboarding.HandoverChecklist',
        on_delete=models.CASCADE,
        related_name='items',
    )

    kind = models.CharField(max_length=15, choices=KINDS, default='otro')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    status = models.CharField(
        max_length=15, choices=STATUSES, default='pendiente', db_index=True,
    )
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivered_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    notes = models.TextField(blank=True)

    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'handover_item'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.get_kind_display()}: {self.name}'

    def mark_delivered(self, *, user=None, notes=''):
        self.status = 'entregado'
        self.delivered_at = timezone.now()
        if user:
            self.delivered_by = user
        if notes:
            self.notes = notes
        self.save(update_fields=[
            'status', 'delivered_at', 'delivered_by', 'notes', 'updated_at',
        ])

    def mark_no_aplica(self, *, notes=''):
        self.status = 'no_aplica'
        if notes:
            self.notes = notes
        self.save(update_fields=['status', 'notes', 'updated_at'])


class SystemsOffboarding(models.Model):
    STATUSES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En revocación'),
        ('completed', 'Completado'),
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

    termination = models.OneToOneField(
        'contracts.Termination',
        on_delete=models.CASCADE,
        related_name='systems_offboarding',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='pending', db_index=True,
    )
    checks = models.JSONField(
        default=dict, blank=True,
        help_text=(
            'Mapa system_code → bool (completado o no). Default keys: '
            'correo, vpn, erp, ad, badge, llaves'
        ),
    )
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'systems_offboarding'
        ordering = ['-created_at']

    def __str__(self):
        return f'Systems offboarding {self.termination_id} ({self.status})'

    def mark_completed(self, *, checks, user=None, notes=''):
        if not checks:
            raise ValidationError('checks payload is required')
        # Todos los flags deben estar verdaderos.
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise ValidationError(
                f'Hay sistemas sin completar: {", ".join(missing)}'
            )
        self.checks = checks
        self.status = 'completed'
        self.completed_at = timezone.now()
        if user:
            self.completed_by = user
        if notes:
            self.notes = notes
        self.save()
