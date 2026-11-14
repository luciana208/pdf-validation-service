"""tags de consul que traefik lee para armar routers, circuit breaker y reintentos"""

from app.config.settings import Settings


def build_traefik_tags(config: Settings) -> list[str]:
    name = config.router_name
    service = config.service_name
    middlewares = f"{name}-cb,{name}-retry"
    tags = [
        "traefik.enable=true",
        f"traefik.http.middlewares.{name}-cb.circuitbreaker.expression={config.circuit_breaker_expression}",
        f"traefik.http.middlewares.{name}-retry.retry.attempts={config.retry_attempts}",
        f"traefik.http.middlewares.{name}-retry.retry.initialinterval={config.retry_initial_interval}",
    ]

    # router interno: solo lo ven los otros servicios por la red de docker
    if config.internal_host:
        tags += [
            f"traefik.http.routers.{name}-internal.rule=Host(`{config.internal_host}`)",
            f"traefik.http.routers.{name}-internal.entrypoints=internal",
            f"traefik.http.routers.{name}-internal.service={service}",
            f"traefik.http.routers.{name}-internal.middlewares={middlewares}",
        ]

    # router publico por https, solo si el servicio se expone afuera
    if config.public_host:
        tags += [
            f"traefik.http.routers.{name}.rule=Host(`{config.public_host}`)",
            f"traefik.http.routers.{name}.entrypoints=https",
            f"traefik.http.routers.{name}.tls=true",
            f"traefik.http.routers.{name}.service={service}",
            f"traefik.http.routers.{name}.middlewares={middlewares}",
        ]
    return tags
