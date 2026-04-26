# -*- coding: utf-8 -*-
"""
Tests para el modelo DocumentosDigitales

Pruebas unitarias para verificar el comportamiento correcto de la propiedad
tamano_archivo_legible, en particular que no mute el valor del campo
tamano_archivo al ser leida.
"""

import pytest
from apps.documents.models import DocumentosDigitales


def make_doc(tamano):
    """Crea una instancia de DocumentosDigitales en memoria sin guardar en DB."""
    obj = DocumentosDigitales.__new__(DocumentosDigitales)
    obj.tamano_archivo = tamano
    return obj


class TestTamanoArchivoLegible:
    """Tests para la propiedad tamano_archivo_legible."""

    def test_tamano_legible_no_muta(self):
        """La propiedad no debe mutar el campo tamano_archivo en la instancia."""
        doc = make_doc(2097152)  # 2 MB en bytes
        _ = doc.tamano_archivo_legible
        assert doc.tamano_archivo == 2097152, (
            "tamano_archivo fue mutado tras leer tamano_archivo_legible"
        )
        _ = doc.tamano_archivo_legible
        assert doc.tamano_archivo == 2097152, (
            "tamano_archivo fue mutado tras segunda lectura de tamano_archivo_legible"
        )

    def test_tamano_legible_idempotent(self):
        """Llamar la propiedad dos veces debe devolver el mismo valor."""
        doc = make_doc(2097152)  # 2 MB
        result1 = doc.tamano_archivo_legible
        result2 = doc.tamano_archivo_legible
        assert result1 == "2.0 MB"
        assert result2 == "2.0 MB", (
            f"Segunda llamada devolvio '{result2}' en lugar de '2.0 MB'"
        )

    def test_tamano_legible_zero(self):
        """Un tamano_archivo de 0 o None debe devolver '0 B'."""
        doc_zero = make_doc(0)
        assert doc_zero.tamano_archivo_legible == "0 B"

        doc_none = make_doc(None)
        assert doc_none.tamano_archivo_legible == "0 B"

    def test_tamano_legible_bytes(self):
        """Un archivo de 512 bytes debe devolver '512.0 B'."""
        doc = make_doc(512)
        assert doc.tamano_archivo_legible == "512.0 B"

    def test_tamano_legible_kb(self):
        """Un archivo de 1536 bytes (1.5 KB) debe devolver '1.5 KB'."""
        doc = make_doc(1536)
        assert doc.tamano_archivo_legible == "1.5 KB"

    def test_tamano_legible_gb(self):
        """Un archivo de 1073741824 bytes (1.0 GB) debe devolver '1.0 GB'."""
        doc = make_doc(1073741824)
        assert doc.tamano_archivo_legible == "1.0 GB"
