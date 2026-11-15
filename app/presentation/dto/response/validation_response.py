"""contrato de salida de una validacion exitosa"""

from pydantic import BaseModel, Field

from app.business.entities.validation_result import ValidationResult


class ValidationResponseDTO(BaseModel):
    checksum: str = Field(description="SHA-256 del archivo.")
    size_bytes: int = Field(description="Tamaño del archivo en bytes.")
    page_count: int = Field(description="Cantidad de paginas.")

    model_config = {"frozen": True}

    @classmethod
    def from_entity(cls, result: ValidationResult) -> "ValidationResponseDTO":
        return cls(checksum=result.checksum, size_bytes=result.size_bytes, page_count=result.page_count)
