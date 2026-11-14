from app.infrastructure.health import HealthReporter
from app.infrastructure.in_flight import InFlightCounter


async def ok() -> bool:
    return True


async def caida() -> bool:
    raise ConnectionError("sin conexion")


async def test_reporte_con_contrato_comun():
    report = await HealthReporter(InFlightCounter()).report()
    assert report["status"] == "ok"
    for key in ("service", "version", "instance_id", "uptime_seconds", "memory_mb", "requests_in_flight", "dependencies"):
        assert key in report


async def test_dependencia_caida_marca_degradado():
    report = await HealthReporter(InFlightCounter(), {"a": ok, "b": caida}).report()
    assert report["status"] == "degraded"
    assert report["dependencies"] == {"a": "ok", "b": "down"}
