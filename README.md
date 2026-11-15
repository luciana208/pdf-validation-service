# pdf-validation-service

Microservicio de **validación** de PDF-extractext. Verifica que el archivo recibido sea un PDF real, que no supere el tamaño máximo y que se pueda abrir, y calcula su checksum SHA-256.

Lo llama el orquestador como primer paso de la Saga de subida. No guarda nada.

## Endpoint

`POST /api/v1/validations`, con el PDF como body binario (`Content-Type: application/pdf`).

```json
{"checksum": "a3f1…", "size_bytes": 102400, "page_count": 3}
```

| Status | Cuándo |
|---|---|
| `200` | El PDF pasó todas las validaciones |
| `400` | Body vacío, no empieza con `%PDF`, está dañado, protegido con contraseña o no tiene páginas |
| `413` | Supera `MAX_PDF_SIZE_MB` |

`GET /health`: estado de la instancia.

## Arquitectura

```
presentation   validation_router · controller · DTO · middlewares · errores RFC 9457
use_cases      ValidatePDFUseCase: tamaño -> firma %PDF -> apertura -> checksum
business       ValidationResult · reglas de tamaño y firma · checksum · puerto IPDFInspector
data           PypdfInspector (pypdf, en memoria)
infrastructure Consul · tags de Traefik · health · instancia
```

## Configuración

Ver `.env.example`. Las propias de este servicio:

| Variable | Por defecto | Descripción |
|---|---|---|
| `MAX_PDF_SIZE_MB` | `10` | Tamaño máximo |
| `INTERNAL_HOST` | `validation.internal` | Nombre interno en Traefik |

## Desarrollo

```bash
uv sync
uv run pytest            # unitarios e integración, no necesitan servicios externos
uv run pytest --cov
GRANIAN_INTERFACE=asgi uv run granian app.main:app --port 8001
```

## Plataforma (igual en los cuatro servicios)

| Pieza | Archivo | Qué hace |
|---|---|---|
| Registro en Consul | `app/infrastructure/consul_registry.py` | Al arrancar registra la instancia con ID único (`<servicio>-<hex>`), su IP, el check HTTP a `/health` y los tags de Traefik. Si Consul no está, reintenta en segundo plano. Al apagarse se da de baja. |
| Tags de Traefik | `app/infrastructure/traefik_tags.py` | Routers interno y público, circuit breaker y reintentos |
| Health | `app/infrastructure/health.py` | Contrato común: `status`, `service`, `version`, `instance_id`, `uptime_seconds`, `memory_mb`, `requests_in_flight`, `dependencies` |
| Errores | `app/presentation/error_handlers.py` | Todo error sale en formato RFC 9457 (`application/problem+json`) |

## Ejecución dentro del sistema completo

Este servicio no se levanta solo en producción: lo levanta `pdf-extractext-deploy` junto con Traefik, Consul y el resto de los servicios.

```bash
cd ../pdf-extractext-deploy
./scripts/up.sh
```

## Imagen Docker

- Multi-stage: `uv` solo está en la etapa de build; la imagen final tiene Python 3.14 slim, el venv y el código.
- Usuario sin privilegios (`appuser`) y zona horaria `America/Argentina/Buenos_Aires`.
- `HEALTHCHECK` contra `/health`.
- Granian toma host, puerto y workers de `GRANIAN_*`, así que el puerto no queda fijo en la imagen.

```bash
docker build -t pdf-extractext/validation:1.0.0 .
```

## Principios aplicados

- **Arquitectura limpia / puertos y adaptadores:** el negocio depende de interfaces y `app/dependencies.py` elige las implementaciones.
- **SOLID, DRY, KISS, YAGNI:** un caso de uso por operación, sin dependencias que no se usan.
- **TDD:** cada cambio arranca con un test que falla.
- **12-Factor:** un repo por servicio (I), dependencias fijadas con `uv.lock` (II), configuración por entorno (III), servicios externos por URL (IV), build y run separados (V), procesos sin estado (VI), port binding (VII), apagado ordenado (IX), logs a stdout (XI).

## Equipo

Fabio, Luciana y Celina — Desarrollo de Software, UTN Facultad Regional San Rafael, 2026.

## Licencia

MIT, ver [LICENSE](LICENSE).
