"""Tests for WordTemplateService field refs + tenant config (B.5b #30, #31, #74)."""
import inspect


class TestWordTemplateServiceFieldRefs:
    def test_no_direct_numero_adenda_access(self):
        """contrato.numero_adenda is AttributeError on Contract (#30 — split L3.10.3)."""
        from apps.documents.services import word_template_service

        src = inspect.getsource(word_template_service)
        # The bug pattern: direct attribute access without getattr default
        assert "contrato.numero_adenda or" not in src
        # And no bare `contrato.numero_adenda` — only contrato.parent_contract or getattr
        assert "'NUMERO_ADENDA': contrato.numero_adenda" not in src

    def test_no_legacy_estado_filter(self):
        """Contract.objects.filter(estado='ACTIVO') is FieldError; field is `status` (#31)."""
        from apps.documents.services import word_template_service

        src = inspect.getsource(word_template_service)
        assert "estado='ACTIVO'" not in src
        assert 'estado="ACTIVO"' not in src

    def test_construir_variables_empleado_accepts_tenant_kwarg(self):
        """Per #74, must accept tenant for Company.get_config lookup."""
        from apps.documents.services.word_template_service import WordTemplateService

        sig = inspect.signature(WordTemplateService.construir_variables_empleado)
        assert "tenant" in sig.parameters

    def test_construir_variables_contrato_accepts_tenant_kwarg(self):
        from apps.documents.services.word_template_service import WordTemplateService

        sig = inspect.signature(WordTemplateService.construir_variables_contrato)
        assert "tenant" in sig.parameters

    def test_construir_variables_certificado_accepts_tenant_kwarg(self):
        from apps.documents.services.word_template_service import WordTemplateService

        sig = inspect.signature(WordTemplateService.construir_variables_certificado)
        assert "tenant" in sig.parameters
