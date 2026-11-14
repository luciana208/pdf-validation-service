"""adaptador de IPDFInspector con pypdf, trabaja en memoria"""

import io
import logging

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.business.domain.exceptions import InvalidPDFError
from app.business.inspectors.interfaces.i_pdf_inspector import IPDFInspector

logger = logging.getLogger(__name__)


class PypdfInspector(IPDFInspector):
    def count_pages(self, file_bytes: bytes) -> int:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            # un pdf con contraseña no se puede procesar despues
            if reader.is_encrypted and not reader.decrypt(""):
                raise InvalidPDFError("el PDF esta protegido con contraseña")
            page_count = len(reader.pages)
        except InvalidPDFError:
            raise
        except (PyPdfError, ValueError, KeyError, TypeError, OSError) as exc:
            logger.warning("no se pudo leer el pdf: %s", exc)
            raise InvalidPDFError("el archivo no es un PDF valido o esta dañado") from exc

        if page_count == 0:
            raise InvalidPDFError("el PDF no tiene paginas")
        return page_count
