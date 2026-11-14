import pytest

from app.business.domain.checksum_calculator import calculate_checksum
from app.business.domain.exceptions import InvalidPDFError, PDFTooLargeError
from app.business.inspectors.interfaces.i_pdf_inspector import IPDFInspector
from app.use_cases.validate_pdf import ValidatePDFUseCase
from tests.pdf_factory import NOT_A_PDF, TEXT_PDF


class FakeInspector(IPDFInspector):
    def __init__(self, pages: int = 1, error: Exception | None = None) -> None:
        self.pages = pages
        self.error = error
        self.calls = 0

    def count_pages(self, file_bytes: bytes) -> int:
        self.calls += 1
        if self.error:
            raise self.error
        return self.pages


async def test_devuelve_checksum_tamaño_y_paginas():
    result = await ValidatePDFUseCase(FakeInspector(pages=4), 10_000).execute(TEXT_PDF)
    assert result.checksum == calculate_checksum(TEXT_PDF)
    assert result.size_bytes == len(TEXT_PDF)
    assert result.page_count == 4


async def test_no_abre_el_pdf_si_no_tiene_firma():
    inspector = FakeInspector()
    with pytest.raises(InvalidPDFError):
        await ValidatePDFUseCase(inspector, 10_000).execute(NOT_A_PDF)
    assert inspector.calls == 0


async def test_no_abre_el_pdf_si_es_muy_grande():
    inspector = FakeInspector()
    with pytest.raises(PDFTooLargeError):
        await ValidatePDFUseCase(inspector, 10).execute(TEXT_PDF)
    assert inspector.calls == 0


async def test_propaga_error_de_lectura():
    inspector = FakeInspector(error=InvalidPDFError("dañado"))
    with pytest.raises(InvalidPDFError):
        await ValidatePDFUseCase(inspector, 10_000).execute(TEXT_PDF)
