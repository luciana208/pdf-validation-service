import pytest

from app.business.domain.exceptions import InvalidPDFError, PDFTooLargeError
from app.business.domain.pdf_rules import ensure_pdf_signature, ensure_within_size
from tests.pdf_factory import NOT_A_PDF, TEXT_PDF


def test_acepta_pdf_con_firma():
    ensure_pdf_signature(TEXT_PDF)


def test_rechaza_archivo_sin_firma_pdf():
    with pytest.raises(InvalidPDFError):
        ensure_pdf_signature(NOT_A_PDF)


def test_rechaza_archivo_vacio():
    with pytest.raises(InvalidPDFError):
        ensure_pdf_signature(b"")


def test_acepta_tamaño_en_el_limite():
    ensure_within_size(b"x" * 100, max_size_bytes=100)


def test_rechaza_tamaño_mayor_al_limite():
    with pytest.raises(PDFTooLargeError):
        ensure_within_size(b"x" * 101, max_size_bytes=100)
