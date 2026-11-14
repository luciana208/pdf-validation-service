from app.business.domain.checksum_calculator import calculate_checksum
from tests.pdf_factory import CORRUPT_PDF, NOT_A_PDF, TEXT_PDF, build_pdf

URL = "/api/v1/validations"
PDF_HEADERS = {"Content-Type": "application/pdf"}


async def test_pdf_valido_devuelve_200_con_checksum(client):
    response = await client.post(URL, content=TEXT_PDF, headers=PDF_HEADERS)
    assert response.status_code == 200
    assert response.json() == {
        "checksum": calculate_checksum(TEXT_PDF),
        "size_bytes": len(TEXT_PDF),
        "page_count": 1,
    }


async def test_archivo_que_no_es_pdf_devuelve_400_problem_json(client):
    response = await client.post(URL, content=NOT_A_PDF, headers=PDF_HEADERS)
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["status"] == 400


async def test_pdf_dañado_devuelve_400(client):
    response = await client.post(URL, content=CORRUPT_PDF, headers=PDF_HEADERS)
    assert response.status_code == 400


async def test_body_vacio_devuelve_400(client):
    response = await client.post(URL, content=b"", headers=PDF_HEADERS)
    assert response.status_code == 400


async def test_pdf_mayor_al_limite_devuelve_413(client):
    # el limite de los tests es 1 MB (tests/conftest.py)
    response = await client.post(URL, content=build_pdf(padding=1024 * 1024), headers=PDF_HEADERS)
    assert response.status_code == 413


async def test_request_muy_grande_se_corta_en_el_middleware(client):
    response = await client.post(URL, content=build_pdf(padding=2 * 1024 * 1024), headers=PDF_HEADERS)
    assert response.status_code == 413
    assert response.headers["content-type"] == "application/problem+json"


async def test_health_responde_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "pdf-validation-service"
    assert response.json()["status"] == "ok"
