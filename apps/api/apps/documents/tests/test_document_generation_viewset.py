"""Tests for DocumentGenerationViewSet stale-consumer fixes (B.5b #22-#27)."""
import inspect


class TestDocumentGenerationViewSetFieldRefs:
    def test_generar_contrato_uses_pk_lookup_not_legacy_field(self):
        """Contract has no `contrato_id` field post-rename — must use pk= lookup (#22)."""
        from api.v1.documents.views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_contrato)
        assert "contrato_id=contrato_id" not in src
        # After fix: pk= or id= lookup
        assert "pk=contrato_id" in src or "id=contrato_id" in src

    def test_generar_certificado_uses_pk_lookup_not_legacy_empleado_id(self):
        """Employee has no `empleado_id` field post-rename (#23)."""
        from api.v1.documents.views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_certificado)
        assert "empleado_id=empleado_id" not in src

    def test_no_documento_documento_id_attribute_access(self):
        """DigitalDocument PK is `id` UUID — `documento.documento_id` is AttributeError (#24)."""
        from api.v1.documents import views as mod

        src = inspect.getsource(mod)
        assert "documento.documento_id" not in src

    def test_subir_plantilla_word_uses_created_by_not_creada_por(self):
        """DocumentTemplate field is `created_by` (#25)."""
        from api.v1.documents.views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.subir_plantilla_word)
        assert "creada_por=" not in src
        assert "created_by=" in src

    def test_generar_desde_plantilla_word_reads_distinct_query_params(self):
        """Two IDs must NOT both read from `id` (#27)."""
        from api.v1.documents.views import DocumentGenerationViewSet

        src = inspect.getsource(DocumentGenerationViewSet.generar_desde_plantilla_word)
        assert (
            'request.data.get("empleado_id")' in src
            or 'request.data.get("empleado")' in src
        )
        assert (
            'request.data.get("contrato_id")' in src
            or 'request.data.get("contrato")' in src
        )
