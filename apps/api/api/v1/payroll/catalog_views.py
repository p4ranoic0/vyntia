"""Read-only catalog viewsets (D.2). Catalog is vendor-managed (seed only)."""

from rest_framework import viewsets

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter

from .catalog_serializers import (
    PayrollConceptSerializer,
    RegimenConfigSerializer,
    TaxParameterSerializer,
)


class TaxParameterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaxParameter.objects.all()
    serializer_class = TaxParameterSerializer
    filterset_fields = ["code", "unit"]


class PayrollConceptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PayrollConcept.objects.all()
    serializer_class = PayrollConceptSerializer
    filterset_fields = ["category", "sunat_code", "is_active"]


class RegimenConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegimenConfig.objects.all()
    serializer_class = RegimenConfigSerializer
    filterset_fields = ["regimen_code"]
