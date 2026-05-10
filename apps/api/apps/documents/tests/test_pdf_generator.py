"""Tests for pdf_generator orphan tenant + signature fixes (B.5b #78 partial)."""
import inspect


class TestPDFGeneratorSignatures:
    def test_generar_pdf_adenda_param_named_amendment_id(self):
        """Post-split L3.10.3, the call expects amendment PK, not contract PK."""
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator.generar_pdf_adenda)
        params = list(sig.parameters.keys())
        assert "adenda_id" in params or "amendment_id" in params

    def test_guardar_documento_digital_accepts_tenant(self):
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator._guardar_documento_digital)
        assert "tenant" in sig.parameters

    def test_generar_pdf_contrato_accepts_tenant(self):
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator.generar_pdf_contrato)
        assert "tenant" in sig.parameters

    def test_generar_pdf_certificado_accepts_tenant(self):
        from apps.documents.services.pdf_generator import PDFGenerator

        sig = inspect.signature(PDFGenerator.generar_pdf_certificado)
        assert "tenant" in sig.parameters
