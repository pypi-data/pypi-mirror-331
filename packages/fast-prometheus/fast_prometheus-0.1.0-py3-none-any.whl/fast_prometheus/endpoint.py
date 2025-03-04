from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route


def generate_latest_metrics(request: Request) -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def create_prometheus_route() -> Mount:
    return Mount("/", routes=[Route("/metrics", endpoint=generate_latest_metrics)])
