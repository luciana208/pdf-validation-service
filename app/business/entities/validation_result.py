from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    # resultado de un pdf que paso todas las validaciones
    checksum: str
    size_bytes: int
    page_count: int
