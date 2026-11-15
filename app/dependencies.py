"""composicion: unico lugar que elige las implementaciones concretas"""

from app.config.settings import settings
from app.data.inspectors.pypdf_inspector import PypdfInspector
from app.presentation.controllers.validation_controller import ValidationController
from app.use_cases.validate_pdf import ValidatePDFUseCase


def get_validation_controller() -> ValidationController:
    return ValidationController(ValidatePDFUseCase(PypdfInspector(), settings.max_pdf_size_bytes))
