"""reglas de formato y tamaño, se mira el contenido y no la extension"""

from app.business.domain.exceptions import InvalidPDFError, PDFTooLargeError

PDF_MAGIC_BYTES = b"%PDF"


def ensure_within_size(file_bytes: bytes, max_size_bytes: int) -> None:
    if len(file_bytes) > max_size_bytes:
        raise PDFTooLargeError(max_size_bytes // (1024 * 1024))


def ensure_pdf_signature(file_bytes: bytes) -> None:
    # todo pdf empieza con %PDF, un .docx renombrado no pasa
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise InvalidPDFError()
