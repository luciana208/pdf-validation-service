import pytest

from app.business.domain.exceptions import InvalidPDFError
from app.data.inspectors.pypdf_inspector import PypdfInspector
from tests.pdf_factory import CORRUPT_PDF, build_pdf


def test_cuenta_las_paginas():
    assert PypdfInspector().count_pages(build_pdf(["uno", "dos", "tres"])) == 3


def test_pdf_dañado_lanza_invalid_pdf():
    with pytest.raises(InvalidPDFError):
        PypdfInspector().count_pages(CORRUPT_PDF)
