from abc import ABC, abstractmethod


class IPDFInspector(ABC):
    """puerto para abrir el pdf y contar paginas, el negocio no conoce la libreria"""

    @abstractmethod
    def count_pages(self, file_bytes: bytes) -> int:
        """devuelve la cantidad de paginas o lanza InvalidPDFError si no se puede leer"""
