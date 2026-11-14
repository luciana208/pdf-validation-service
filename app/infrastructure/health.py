"""armado del reporte de salud con el contrato comun a todos los servicios"""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.config.settings import settings
from app.infrastructure.in_flight import InFlightCounter
from app.infrastructure.instance import INSTANCE_ID, uptime_seconds

logger = logging.getLogger(__name__)

DependencyCheck = Callable[[], Awaitable[bool]]


def memory_mb() -> float:
    # memoria residente del proceso leida de /proc (0 si no esta disponible)
    try:
        with open("/proc/self/status", encoding="ascii") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024, 1)
    except OSError:
        pass
    return 0.0


class HealthReporter:
    def __init__(self, in_flight: InFlightCounter, checks: dict[str, DependencyCheck] | None = None) -> None:
        self._in_flight = in_flight
        self._checks = checks or {}

    async def report(self) -> dict:
        dependencies = await self._check_dependencies()
        status = "ok" if all(value == "ok" for value in dependencies.values()) else "degraded"
        return {
            "status": status,
            "service": settings.service_name,
            "version": settings.service_version,
            "instance_id": INSTANCE_ID,
            "uptime_seconds": uptime_seconds(),
            "memory_mb": memory_mb(),
            "requests_in_flight": self._in_flight.count,
            "dependencies": dependencies,
        }

    async def _check_dependencies(self) -> dict[str, str]:
        names = list(self._checks)
        results = await asyncio.gather(*(self._run(self._checks[name]) for name in names))
        return dict(zip(names, results))

    @staticmethod
    async def _run(check: DependencyCheck) -> str:
        # una dependencia caida no tumba el health, solo lo marca como degradado
        try:
            return "ok" if await check() else "down"
        except Exception as exc:
            logger.warning("chequeo de dependencia fallido: %s", exc)
            return "down"
