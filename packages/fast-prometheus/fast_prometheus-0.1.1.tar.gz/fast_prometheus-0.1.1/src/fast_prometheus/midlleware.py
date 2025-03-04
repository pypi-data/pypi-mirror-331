import time
from collections.abc import Mapping

from starlette.middleware import Middleware
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response
from starlette.routing import Match, Mount, Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from fast_prometheus.config import MetricConfig
from fast_prometheus.executor import AfterData, BeforeData, ErrorData
from fast_prometheus.registry import ExecutorRegistry


def _get_path(scope: Scope, routes: list[Route]) -> list[str] | None:
    for route in routes:
        match, child_scope = route.matches(scope)
        if match == Match.FULL:
            parts = [route.path]
            if isinstance(route, Mount) and route.routes:
                child_scope = {**scope, **child_scope}
                child_parts = _get_path(child_scope, route.routes)
                if child_parts is None:
                    return None
                parts.extend(child_parts)
            return parts
        elif match == Match.PARTIAL:
            remaining_routes = routes[routes.index(route) + 1 :]
            full_parts = _get_path(scope, remaining_routes)
            if full_parts is not None:
                return full_parts
            else:
                return [route.path]
    return None


def get_full_path(request: HTTPConnection) -> str | None:
    app = request.app
    scope = request.scope
    route_parts = _get_path(scope, app.routes)
    path = "".join(route_parts) if route_parts else None

    if not path and app.router.redirect_slashes and scope["path"] != "/":
        is_trailing_slash = scope["path"].endswith("/")
        new_path = scope["path"][:-1] if is_trailing_slash else scope["path"] + "/"
        redirect_scope = {**scope, "path": new_path}
        redirect_parts = _get_path(redirect_scope, app.routes)
        if redirect_parts:
            adjusted = new_path if is_trailing_slash else new_path.rstrip("/")
            path = adjusted

    return path


class FastPrometheusMiddleware:
    def __init__(self, app: ASGIApp, registry: ExecutorRegistry) -> None:
        self.app = app
        self.registry = registry

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()
        request = Request(scope, receive, send)
        path = get_full_path(request) or request.url.path

        await self.registry.before_execute(
            data=BeforeData(
                request=request, path=path, method=request.method, start_time=start_time
            )
        )
        status_code: int = 500
        body: bytes = b""
        headers: Mapping[str, str] | None = None

        try:

            async def send_wrapper(message: Message) -> None:
                if message["type"] == "http.response.start":
                    nonlocal headers
                    nonlocal status_code
                    headers = {
                        k.lower().decode("latin-1"): v.decode("latin-1")
                        for k, v in message["headers"]
                    }
                    status_code = message["status"]
                    if message["type"] == "http.response.body" and message["body"]:
                        nonlocal body
                        body += message["body"]
                await send(message)

            await self.app(scope, receive, send_wrapper)

        except Exception as exc:
            await self.registry.error_execute(
                data=ErrorData(
                    reques=request, start_time=start_time, method=request.method, path=path
                )
            )
            raise exc

        finally:
            request = Request(scope, receive, send)
            response = Response(content=body, status_code=status_code, headers=headers)
            await self.registry.after_execute(
                data=AfterData(
                    request=request,
                    response=response,
                    start_time=start_time,
                    method=request.method,
                    path=path,
                    status_code=response.status_code,
                )
            )


def create_prometheus_midlleware(
    app_name: str = "app",
    metrics: list[MetricConfig] | None = None,
    append_golden_signals: bool = True,
) -> Middleware:
    registry = ExecutorRegistry(app_name)
    if append_golden_signals:
        registry.init_golden_signals()
    if metrics:
        registry.add_all(metrics)

    return Middleware(FastPrometheusMiddleware, registry=registry)
