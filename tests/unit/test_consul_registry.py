import json

import httpx

from app.config.settings import Settings
from app.infrastructure.consul_registry import ConsulRegistry


def make_registry(handler) -> ConsulRegistry:
    config = Settings(service_name="pdf-validation-service", service_address="10.0.0.5", port=8000)
    client = httpx.AsyncClient(base_url="http://consul:8500", transport=httpx.MockTransport(handler))
    return ConsulRegistry(config, client, "pdf-validation-service-abc123")


async def test_registra_con_id_unico_check_y_tags():
    sent = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent["path"] = request.url.path
        sent["body"] = json.loads(request.content)
        return httpx.Response(200)

    registry = make_registry(handler)
    await registry.register()

    assert sent["path"] == "/v1/agent/service/register"
    assert sent["body"]["ID"] == "pdf-validation-service-abc123"
    assert sent["body"]["Name"] == "pdf-validation-service"
    assert sent["body"]["Address"] == "10.0.0.5"
    assert sent["body"]["Check"]["HTTP"] == "http://10.0.0.5:8000/health"
    assert "traefik.enable=true" in sent["body"]["Tags"]
    assert registry.registered


async def test_baja_usa_el_id_de_la_instancia():
    paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        return httpx.Response(200)

    registry = make_registry(handler)
    await registry.register()
    await registry.stop()

    assert paths[-1] == "/v1/agent/service/deregister/pdf-validation-service-abc123"
    assert not registry.registered


async def test_stop_sin_registro_previo_no_llama_a_consul():
    calls = []
    registry = make_registry(lambda request: calls.append(request) or httpx.Response(200))
    await registry.stop()
    assert calls == []
