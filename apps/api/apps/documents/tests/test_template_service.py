"""Tests for TemplateService stale-consumer fixes (B.5b #28, #29 + cluster)."""
import inspect


class TestTemplateServiceFieldRefs:
    def test_no_legacy_get_estado_display(self):
        """Contract field renamed to `status`; auto-method is get_status_display (#28)."""
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        assert ".get_estado_display()" not in src
        # Positive: the rename target exists somewhere in the module
        assert ".get_status_display()" in src

    def test_no_legacy_creado_por_id_attr(self):
        """Python attr is created_by_id, not creado_por_id (#29).

        The legacy db_column may still be `creado_por_id` in the model
        Meta, but accessing the attribute uses the Python field name
        `created_by_id`.
        """
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        assert ".creado_por_id" not in src

    def test_no_legacy_contrato_id_attr_access(self):
        """Contract PK is `id` UUID. Variable name `contrato_id` (param)
        is fine; `<contract_obj>.contrato_id` is AttributeError."""
        from apps.documents.services import template_service

        src = inspect.getsource(template_service)
        # The bug pattern is `c.contrato_id` or similar attribute access
        assert "c.contrato_id" not in src
        assert "contrato.contrato_id" not in src

    def test_obtener_datos_institucion_accepts_tenant(self):
        """Per #75, must accept tenant kwarg."""
        from apps.documents.services.template_service import TemplateService

        sig = inspect.signature(TemplateService._obtener_datos_institucion)
        assert "tenant" in sig.parameters
