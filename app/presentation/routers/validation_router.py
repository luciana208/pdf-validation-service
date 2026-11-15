"""endpoint de validacion (/api/v1/validations)"""

from fastapi import APIRouter, Depends, Request, status

from app.dependencies import get_validation_controller
from app.presentation.controllers.validation_controller import ValidationController
from app.presentation.dto.response.validation_response import ValidationResponseDTO

router = APIRouter(prefix="/api/v1/validations", tags=["validations"])

# el pdf viaja como body binario, se documenta a mano en openapi
PDF_BODY = {"requestBody": {"required": True, "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}}}}


@router.post(
    "",
    response_model=ValidationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Validar un PDF",
    openapi_extra=PDF_BODY,
)
async def validate_pdf(
    request: Request,
    controller: ValidationController = Depends(get_validation_controller),
) -> ValidationResponseDTO:
    """
    valida formato, tamaño y que el pdf se pueda abrir; devuelve checksum y paginas.
    errores: 400 si no es un pdf valido, 413 si supera el tamaño maximo.
    """
    file_bytes = await request.body()
    return await controller.validate(file_bytes)
