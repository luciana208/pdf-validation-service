"""traduccion de errores a respuestas http con el formato rfc 9457 (problem details)"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.business.domain.exceptions import DomainError, InvalidPDFError, PDFTooLargeError

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"

# unico lugar que sabe que status corresponde a cada error de negocio
_HTTP_STATUS: dict[type[DomainError], tuple[int, str]] = {
    InvalidPDFError: (400, "Bad Request"),
    PDFTooLargeError: (413, "Payload Too Large"),
}
_DEFAULT_STATUS = (400, "Bad Request")


def problem_detail_response(status: int, title: str, detail: str, instance: str) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail, "instance": instance}
    return JSONResponse(status_code=status, content=body, media_type=PROBLEM_JSON)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status, title = _HTTP_STATUS.get(type(exc), _DEFAULT_STATUS)
    return problem_detail_response(status, title, str(exc), str(request.url))


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail = "; ".join(f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in exc.errors())
    return problem_detail_response(422, "Unprocessable Content", detail, str(request.url))


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem_detail_response(exc.status_code, str(exc.detail), str(exc.detail), str(request.url))


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("error no controlado")
    return problem_detail_response(500, "Internal Server Error", "error interno del servicio", str(request.url))


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
