# -*- coding: utf-8 -*-
"""
Integration tests for PDF generation pipeline.

These tests verify that:
- PDFs contain actual document content (not the "DOCUMENTO GENERADO" stub)
- PDFs are larger than 5000 bytes (real content, not near-empty)
- The engine configuration reports xhtml2pdf as preferred motor
- Fallback paths log WARNING before falling through (not silently swallowed)
"""

import logging
import pytest

from app_rrhh.services.pdf_generator import PDFGenerator

# Minimal HTML used across tests — contains a unique marker to verify real rendering
MINIMAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; font-size: 12px; }
        h1 { text-align: center; }
        p { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Certificado Laboral</h1>
    <p>Se certifica que el trabajador <strong>EMPLEADO_TEST_12345678</strong> presta servicios
    en esta institucion desde el 01 de enero de 2020.</p>
    <p>El trabajador desempena el cargo de Asistente Administrativo en el area de Recursos Humanos.</p>
    <p>La remuneracion mensual asciende a S/ 2,500.00 (Dos mil quinientos y 00/100 soles).</p>
    <p>Se expide el presente certificado a solicitud del interesado para los fines que estime
    conveniente.</p>
    <br>
    <p>Lima, 13 de marzo de 2026</p>
    <br>
    <p>_______________________________</p>
    <p>Director de Recursos Humanos</p>
</body>
</html>
"""

MULTI_PARAGRAPH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>body { font-family: Arial; font-size: 11px; margin: 2cm; }</style>
</head>
<body>
""" + "\n".join(
    f"<p>Parrafo de contenido numero {i}. Este parrafo contiene texto representativo del contenido real de un documento laboral de recursos humanos.</p>"
    for i in range(1, 30)
) + """
</body>
</html>
"""


class TestPDFNotStub:
    """Test that generated PDFs contain real content, not the ReportLab stub."""

    def test_pdf_not_stub(self):
        """PDF bytes must NOT contain the stub marker 'DOCUMENTO GENERADO'."""
        generator = PDFGenerator()
        pdf_bytes = generator._html_to_pdf(MINIMAL_HTML)

        assert b"DOCUMENTO GENERADO" not in pdf_bytes, (
            "PDF contains the ReportLab stub marker 'DOCUMENTO GENERADO' — "
            "this means xhtml2pdf failed and fell through to the stub engine. "
            f"PDF size: {len(pdf_bytes)} bytes."
        )

    def test_pdf_contains_content(self):
        """PDF bytes should contain the unique marker from the HTML input.

        xhtml2pdf embeds source text as readable bytes in most cases.
        If font subsetting makes text non-searchable in raw bytes,
        we fall back to asserting size > 5000 and absence of stub marker.
        """
        generator = PDFGenerator()
        pdf_bytes = generator._html_to_pdf(MINIMAL_HTML)

        # Primary assertion: unique marker visible in raw bytes
        marker_found = b"EMPLEADO_TEST_12345678" in pdf_bytes

        if not marker_found:
            # Fallback: accept if PDF is large enough and stub-free
            assert len(pdf_bytes) > 5000, (
                f"PDF is only {len(pdf_bytes)} bytes — likely a near-empty stub. "
                "Expected real content rendering."
            )
            assert b"DOCUMENTO GENERADO" not in pdf_bytes, (
                "PDF contains stub marker and unique marker was not found — "
                "xhtml2pdf fallback to stub detected."
            )
        else:
            assert marker_found, (
                "Unique marker 'EMPLEADO_TEST_12345678' not found in PDF bytes — "
                "content was not rendered from the HTML template."
            )

    def test_pdf_minimum_size(self):
        """PDF generated from multi-paragraph HTML must be larger than 5000 bytes."""
        generator = PDFGenerator()
        pdf_bytes = generator._html_to_pdf(MULTI_PARAGRAPH_HTML)

        assert len(pdf_bytes) > 5000, (
            f"PDF is only {len(pdf_bytes)} bytes — expected > 5000 bytes for "
            "real content. This likely indicates the stub engine was used."
        )


class TestEngineConfiguration:
    """Test engine configuration reporting."""

    def test_config_reports_xhtml2pdf(self):
        """obtener_configuracion_disponible() must report xhtml2pdf as motor_preferido
        on this Windows machine where xhtml2pdf is available and WeasyPrint is not.
        """
        generator = PDFGenerator()
        config = generator.obtener_configuracion_disponible()

        assert config['motor_preferido'] == 'xhtml2pdf', (
            f"Expected motor_preferido='xhtml2pdf' but got '{config['motor_preferido']}'. "
            "The config must reflect that xhtml2pdf is the primary engine, "
            "not WeasyPrint (unavailable on Windows) or ReportLab (stub only)."
        )


class TestFallbackLogging:
    """Test that fallback paths log warnings instead of silently swallowing exceptions."""

    def test_xhtml2pdf_logs_warning_on_fallback(self, monkeypatch, caplog):
        """When xhtml2pdf raises, _html_to_pdf must log a WARNING before falling through."""
        generator = PDFGenerator()

        # Make xhtml2pdf raise an exception to trigger the fallback path
        def mock_xhtml2pdf_fail(html_content):
            raise RuntimeError("Simulated xhtml2pdf failure for test")

        monkeypatch.setattr(generator, '_html_to_pdf_xhtml2pdf', mock_xhtml2pdf_fail)

        # Capture log output at WARNING level and above
        with caplog.at_level(logging.WARNING, logger='app_rrhh.services.pdf_generator'):
            # _html_to_pdf will call xhtml2pdf (raises), then WeasyPrint (unavailable),
            # then fall through to ReportLab stub
            result = generator._html_to_pdf(MINIMAL_HTML)

        # Verify a WARNING was logged for the xhtml2pdf failure
        warning_messages = [
            record.message for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert any("xhtml2pdf" in msg for msg in warning_messages), (
            f"Expected a WARNING log mentioning 'xhtml2pdf' but got: {warning_messages}. "
            "Fallback must not be silently swallowed — it must be logged."
        )
