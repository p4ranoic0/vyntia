"""DocumentGenerationViewSet routing migration (B.5b #76)."""


class TestDocumentGenerationRouting:
    def test_view_set_lives_in_documents_module(self):
        """Module migration smoke test (#76 — moved from app_rrhh/ to documents/)."""
        from api.v1.documents import views as docs_views

        assert hasattr(docs_views, "DocumentGenerationViewSet")

    def test_legacy_app_rrhh_module_is_removed(self):
        """Verify the legacy module is gone — import must fail."""
        try:
            from api.v1.app_rrhh import document_generation_views  # noqa: F401
        except ImportError:
            return
        raise AssertionError(
            "api.v1.app_rrhh.document_generation_views still importable — "
            "B.5b #76 migration incomplete"
        )
