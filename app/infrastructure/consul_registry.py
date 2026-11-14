"""alta y baja de la instancia en consul (service discovery)"""

import asyncio
import logging
import socket

import httpx

from app.config.settings import Settings
from app.infrastructure.traefik_tags import build_traefik_tags

logger = logging.getLogger(__name__)

MAX_RETRY_DELAY_SECONDS = 30


def resolve_address(config: Settings) -> str:
    # ip del contenedor en la red de docker, salvo que venga fijada por entorno
    return config.service_address or socket.gethostbyname(socket.gethostname())


class ConsulRegistry:
    def __init__(self, config: Settings, client: httpx.AsyncClient, instance_id: str) -> None:
        self._config = config
        self._client = client
        self._instance_id = instance_id
        self._task: asyncio.Task | None = None
        self.registered = False

    def payload(self) -> dict:
        address = resolve_address(self._config)
        return {
            "ID": self._instance_id,
            "Name": self._config.service_name,
            "Address": address,
            "Port": self._config.port,
            "Tags": build_traefik_tags(self._config),
            "Meta": {"version": self._config.service_version},
            "Check": {
                "HTTP": f"http://{address}:{self._config.port}/health",
                "Interval": self._config.health_check_interval,
                "Timeout": "3s",
                "DeregisterCriticalServiceAfter": "1m",
            },
        }

    async def register(self) -> None:
        response = await self._client.put("/v1/agent/service/register", json=self.payload())
        response.raise_for_status()
        self.registered = True
        logger.info("instancia registrada en consul: %s", self._instance_id)

    async def deregister(self) -> None:
        if not self.registered:
            return
        response = await self._client.put(f"/v1/agent/service/deregister/{self._instance_id}")
        response.raise_for_status()
        self.registered = False
        logger.info("instancia dada de baja en consul: %s", self._instance_id)

    def start(self) -> None:
        # el registro corre en segundo plano para no frenar el arranque si consul no esta
        self._task = asyncio.create_task(self._register_with_retry())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        try:
            await self.deregister()
        except httpx.HTTPError as exc:
            logger.warning("no se pudo dar de baja en consul: %s", exc)

    async def _register_with_retry(self) -> None:
        delay = 1
        while not self.registered:
            try:
                await self.register()
            except httpx.HTTPError as exc:
                logger.warning("consul no disponible (%s), reintento en %ss", exc, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY_SECONDS)


def build_consul_client(config: Settings) -> httpx.AsyncClient:
    headers = {"X-Consul-Token": config.consul_token} if config.consul_token else {}
    return httpx.AsyncClient(base_url=config.consul_url, headers=headers, timeout=5.0)
