"""Serializers for B.6 Position + Plaza + reference data API.

B.8 extends with PositionRegister + PositionRegisterEntry serializers
(CPE / CAP) and the MPP rendering input serializers.
"""
from rest_framework import serializers

from apps.organization.models import (
    CIUOCode,
    OccupationalCategory,
    Plaza,
    Position,
    PositionFunction,
    PositionProfile,
    PositionRegister,
    PositionRegisterEntry,
    PositionRequirement,
    PositionRiskProfile,
)


class OccupationalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupationalCategory
        fields = ['id', 'code', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class CIUOCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIUOCode
        fields = ['id', 'code', 'name', 'description', 'big_group', 'is_active']
        read_only_fields = ['id']


class PositionFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionFunction
        fields = ['id', 'position', 'description', 'is_primary', 'order']
        read_only_fields = ['id']


class PositionRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionRequirement
        fields = ['id', 'position', 'kind', 'description', 'is_required']
        read_only_fields = ['id']


class PositionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionProfile
        fields = [
            'id', 'position',
            'mission', 'technical_competencies', 'soft_competencies',
            'work_conditions', 'kpis',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionRiskProfileSerializer(serializers.ModelSerializer):
    overall_level_display = serializers.CharField(
        source='get_overall_level_display', read_only=True
    )

    class Meta:
        model = PositionRiskProfile
        fields = [
            'id', 'position',
            'overall_level', 'overall_level_display',
            'risk_factors', 'notes',
            'requires_medical_exam', 'requires_iperc',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.nombre_completo', read_only=True
    )
    occupational_category_name = serializers.CharField(
        source='occupational_category.name', read_only=True
    )
    ciuo_code_name = serializers.CharField(
        source='ciuo_code.name', read_only=True
    )
    has_successors = serializers.BooleanField(read_only=True)

    class Meta:
        model = Position
        fields = [
            'id', 'tenant',
            'code', 'name', 'description',
            'version', 'parent_version', 'effective_date', 'is_current',
            'department', 'department_name',
            'occupational_category', 'occupational_category_name',
            'ciuo_code', 'ciuo_code_name',
            'reports_to',
            'is_active',
            'has_successors',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = [
            'id', 'version', 'parent_version', 'is_current',
            'has_successors', 'created_at', 'updated_at',
        ]


class PositionNewVersionSerializer(serializers.Serializer):
    """Input serializer for the `new_version` custom action.

    Accepts UUIDs for related fields (department, occupational_category,
    ciuo_code, reports_to) — they are resolved in the ViewSet via
    `validated_data`. This avoids requiring full DRF-relational queryset
    wiring at serializer-class load time.
    """
    effective_date = serializers.DateField(required=False)
    name = serializers.CharField(required=False, max_length=200)
    department = serializers.UUIDField(required=False, allow_null=True)
    occupational_category = serializers.UUIDField(required=False, allow_null=True)
    ciuo_code = serializers.UUIDField(required=False, allow_null=True)
    reports_to = serializers.UUIDField(required=False, allow_null=True)


class PlazaSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    position_code = serializers.CharField(source='position.code', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    current_employee_name = serializers.CharField(
        source='current_employee.nombre_completo', read_only=True
    )

    class Meta:
        model = Plaza
        fields = [
            'id', 'tenant',
            'code',
            'position', 'position_code', 'position_name',
            'current_employee', 'current_employee_name',
            'status', 'status_display',
            'opened_at', 'closed_at', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlazaOccupySerializer(serializers.Serializer):
    """Input for `occupy` custom action — Employee UUID resolved in ViewSet."""
    employee = serializers.UUIDField()


# ---- B.8 — PositionRegister (CPE + CAP) -------------------------------------

class PositionRegisterEntrySerializer(serializers.ModelSerializer):
    position_code = serializers.CharField(source='position.code', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    situacion_display = serializers.CharField(
        source='get_situacion_display', read_only=True,
    )
    clasificacion_cap_display = serializers.CharField(
        source='get_clasificacion_cap_display', read_only=True,
    )

    class Meta:
        model = PositionRegisterEntry
        fields = [
            'id', 'register', 'position', 'position_code', 'position_name',
            'sequence', 'plaza_code', 'plaza_count',
            'situacion', 'situacion_display',
            'nivel_organizacional', 'nivel_remunerativo',
            'clasificacion_cap', 'clasificacion_cap_display',
            'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionRegisterSerializer(serializers.ModelSerializer):
    register_type_display = serializers.CharField(
        source='get_register_type_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    entry_count = serializers.SerializerMethodField()

    class Meta:
        model = PositionRegister
        fields = [
            'id', 'tenant',
            'register_type', 'register_type_display',
            'title', 'description',
            'version', 'parent_version',
            'status', 'status_display',
            'effective_date', 'approved_at', 'approved_by',
            'servir_registered_at', 'servir_registration_ref',
            'entry_count',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = [
            'id', 'version', 'parent_version',
            'approved_at', 'approved_by',
            'servir_registered_at', 'servir_registration_ref',
            'entry_count', 'created_at', 'updated_at',
        ]

    def get_entry_count(self, obj):
        return obj.entries.count()


class PositionRegisterApprovalSerializer(serializers.Serializer):
    """Input for PositionRegister approve action."""
    effective_date = serializers.DateField(required=False)


class PositionRegisterServirSerializer(serializers.Serializer):
    """Input for PositionRegister register-in-servir action (CPE only)."""
    reference = serializers.CharField(max_length=100)
