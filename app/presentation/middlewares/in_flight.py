"""middleware que cuenta las requests abiertas para el health check"""

from starlette.types import ASGIApp, Receive, Scope, Send

from app.infrastructure.in_flight import InFlightCounter


class InFlightMiddleware:
    def __init__(self, app: ASGIApp, counter: InFlightCounter) -> None:
        self.app = app
        self.counter = counter

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # el propio /health no se cuenta
        if scope["type"] != "http" or scope.get("path") == "/health":
            await self.app(scope, receive, send)
            return
        self.counter.increment()
        try:
            await self.app(scope, receive, send)
        finally:
            self.counter.decrement()
