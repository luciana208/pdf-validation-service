"""endpoint de salud que consultan consul, docker y traefik"""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado de la instancia")
async def health(request: Request) -> dict:
    # siempre 200: si una dependencia esta caida se informa como degradado
    return await request.app.state.health.report()
