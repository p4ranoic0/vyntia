"""Serializers for B.7 CCF + audit + Excel API."""
from rest_framework import serializers

from apps.compensation.models import (
    Category,
    CategoryFactorScore,
    CategoryFunctionTable,
    JobFactor,
    JobSubfactor,
    SalaryBand,
)


class JobFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobFactor
        fields = ['id', 'kind', 'name', 'description', 'weight', 'is_active']
        read_only_fields = ['id']


class JobSubfactorSerializer(serializers.ModelSerializer):
    factor_name = serializers.CharField(source='factor.name', read_only=True)
    factor_kind = serializers.CharField(source='factor.kind', read_only=True)

    class Meta:
        model = JobSubfactor
        fields = [
            'id', 'factor', 'factor_name', 'factor_kind',
            'code', 'name', 'description', 'max_score', 'is_active',
        ]
        read_only_fields = ['id']


class CategoryFunctionTableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_count = serializers.SerializerMethodField()

    class Meta:
        model = CategoryFunctionTable
        fields = [
            'id', 'tenant', 'title', 'description',
            'version', 'parent_version', 'status', 'status_display',
            'effective_date', 'approved_at', 'approved_by',
            'category_count',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = [
            'id', 'version', 'parent_version', 'approved_at', 'approved_by',
            'category_count', 'created_at', 'updated_at',
        ]

    def get_category_count(self, obj):
        return obj.categories.count()


class CategorySerializer(serializers.ModelSerializer):
    ccf_title = serializers.CharField(source='ccf.title', read_only=True)
    has_salary_band = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'tenant', 'ccf', 'ccf_title',
            'code', 'name', 'description', 'functions_summary',
            'min_education', 'min_experience_years',
            'technical_competencies', 'soft_competencies',
            'physical_conditions',
            'total_score',
            'is_active',
            'has_salary_band',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_score', 'created_at', 'updated_at']

    def get_has_salary_band(self, obj):
        return hasattr(obj, 'salary_band')


class CategoryFactorScoreSerializer(serializers.ModelSerializer):
    subfactor_code = serializers.CharField(source='subfactor.code', read_only=True)
    subfactor_name = serializers.CharField(source='subfactor.name', read_only=True)
    factor_kind = serializers.CharField(source='subfactor.factor.kind', read_only=True)

    class Meta:
        model = CategoryFactorScore
        fields = [
            'id', 'category', 'subfactor',
            'subfactor_code', 'subfactor_name', 'factor_kind',
            'score', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalaryBandSerializer(serializers.ModelSerializer):
    category_code = serializers.CharField(source='category.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SalaryBand
        fields = [
            'id', 'category', 'category_code', 'category_name',
            'min_salary', 'mid_salary', 'max_salary', 'currency',
            'placement_criteria',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CCFApprovalSerializer(serializers.Serializer):
    """Input for CCF approve action."""
    effective_date = serializers.DateField(required=False)


class CCFExcelImportSerializer(serializers.Serializer):
    """Input for CCF Excel import endpoint."""
    file = serializers.FileField()
    ccf_title = serializers.CharField(max_length=200)
