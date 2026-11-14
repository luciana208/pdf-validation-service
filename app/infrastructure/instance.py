"""identidad de la instancia (replica) que esta corriendo"""

import time
import uuid

from app.config.settings import settings

# id unico por replica: nombre del servicio + sufijo aleatorio
INSTANCE_ID = f"{settings.service_name}-{uuid.uuid4().hex[:8]}"
STARTED_AT = time.monotonic()


def uptime_seconds() -> float:
    return round(time.monotonic() - STARTED_AT, 1)
