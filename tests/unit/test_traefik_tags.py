from app.config.settings import Settings
from app.infrastructure.traefik_tags import build_traefik_tags


def test_router_interno_con_circuit_breaker_y_reintentos():
    tags = build_traefik_tags(Settings(router_name="validation", internal_host="validation.internal", public_host=""))
    assert "traefik.enable=true" in tags
    assert "traefik.http.routers.validation-internal.rule=Host(`validation.internal`)" in tags
    assert "traefik.http.routers.validation-internal.entrypoints=internal" in tags
    assert "traefik.http.routers.validation-internal.middlewares=validation-cb,validation-retry" in tags
    assert any(tag.startswith("traefik.http.middlewares.validation-cb.circuitbreaker.expression=") for tag in tags)
    assert "traefik.http.middlewares.validation-retry.retry.attempts=3" in tags


def test_sin_host_publico_no_hay_router_https():
    tags = build_traefik_tags(Settings(router_name="validation", public_host=""))
    assert not any(".routers.validation.rule" in tag for tag in tags)


def test_con_host_publico_agrega_router_https_con_tls():
    tags = build_traefik_tags(Settings(router_name="validation", public_host="validation.pdfextractext.localhost"))
    assert "traefik.http.routers.validation.entrypoints=https" in tags
    assert "traefik.http.routers.validation.tls=true" in tags
