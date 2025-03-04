from starlette.applications import Starlette

from fast_prometheus.config import MetricConfig
from fast_prometheus.endpoint import create_prometheus_route
from fast_prometheus.executor import AfterData, BeforeData, ErrorData, Executor
from fast_prometheus.midlleware import FastPrometheusMiddleware, create_prometheus_midlleware
from fast_prometheus.registry import ExecutorRegistry

__all__ = [
    "AfterData",
    "BeforeData",
    "ErrorData",
    "Executor",
    "ExecutorRegistry",
    "FastPrometheusMiddleware",
    "MetricConfig",
    "create_prometheus_metrics",
    "create_prometheus_midlleware",
    "create_prometheus_route",
]


def create_prometheus_metrics(
    app: Starlette,
    app_name: str = "app",
    metrics: list[MetricConfig] | None = None,
    append_golden_signals: bool = True,
) -> None:
    midlleware = create_prometheus_midlleware(app_name, metrics, append_golden_signals)
    route = create_prometheus_route()
    app.routes.append(route)
    app.user_middleware.append(midlleware)
