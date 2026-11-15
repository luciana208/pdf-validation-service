from app.presentation.dto.response.validation_response import ValidationResponseDTO
from app.use_cases.validate_pdf import ValidatePDFUseCase


class ValidationController:
    """traduce entre http y el caso de uso"""

    def __init__(self, validate_pdf: ValidatePDFUseCase) -> None:
        self._validate_pdf = validate_pdf

    async def validate(self, file_bytes: bytes) -> ValidationResponseDTO:
        result = await self._validate_pdf.execute(file_bytes)
        return ValidationResponseDTO.from_entity(result)
