"""errores de negocio, no conocen http ni fastapi"""


class DomainError(Exception):
    """base de todos los errores de negocio"""


class InvalidPDFError(DomainError):
    def __init__(self, detail: str = "el archivo no es un PDF valido") -> None:
        super().__init__(detail)


class PDFTooLargeError(DomainError):
    def __init__(self, max_size_mb: int) -> None:
        super().__init__(f"el archivo supera el tamaño maximo de {max_size_mb} MB")
        self.max_size_mb = max_size_mb
