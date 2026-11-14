import asyncio

from app.business.domain.checksum_calculator import calculate_checksum
from app.business.domain.pdf_rules import ensure_pdf_signature, ensure_within_size
from app.business.entities.validation_result import ValidationResult
from app.business.inspectors.interfaces.i_pdf_inspector import IPDFInspector


class ValidatePDFUseCase:
    """tamaño -> firma %PDF -> que se pueda abrir -> checksum"""

    def __init__(self, inspector: IPDFInspector, max_size_bytes: int) -> None:
        self._inspector = inspector
        self._max_size_bytes = max_size_bytes

    async def execute(self, file_bytes: bytes) -> ValidationResult:
        ensure_within_size(file_bytes, self._max_size_bytes)
        ensure_pdf_signature(file_bytes)

        # abrir el pdf es cpu, se hace en un hilo para no frenar el event loop
        page_count = await asyncio.to_thread(self._inspector.count_pages, file_bytes)

        return ValidationResult(
            checksum=calculate_checksum(file_bytes),
            size_bytes=len(file_bytes),
            page_count=page_count,
        )
