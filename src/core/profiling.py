from pyinstrument import Profiler
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from core.settings import settings


class ProfilingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        if not request.query_params.get("profile") or not settings.DEBUG:
            await self.app(scope, receive, send)
            return

        async def discard_send(message: object) -> None:
            pass

        profiler = Profiler(async_mode="enabled")
        profiler.start()
        await self.app(scope, receive, discard_send)
        profiler.stop()

        response = HTMLResponse(profiler.output_html())
        await response(scope, receive, send)
