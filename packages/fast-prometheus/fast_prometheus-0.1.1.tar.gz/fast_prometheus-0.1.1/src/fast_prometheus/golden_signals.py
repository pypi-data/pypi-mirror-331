import time

from prometheus_client.metrics import Counter, Gauge, Histogram

from fast_prometheus.config import MetricConfig
from fast_prometheus.executor import AfterData, BeforeData, ErrorData, Executor
from fast_prometheus.saturation import Saturation, saturation_collector


class RequestTotal(Executor):
    metric: Counter

    def after_execute(self, data: AfterData) -> None:
        self.metric.labels(data.method, data.path, data.status_code).inc()


class ActiveRequestsTotal(Executor):
    metric: Gauge

    def before_execute(self, data: BeforeData) -> None:
        self.metric.labels(data.method, data.path).inc()

    def after_execute(self, data: AfterData) -> None:
        self.metric.labels(data.method, data.path).dec()


class RequestDurationSeconds(Executor):
    metric: Histogram

    def after_execute(self, data: AfterData) -> None:
        latency = time.time() - data.start_time
        self.metric.labels(data.method, data.path, data.status_code).observe(latency)


class ErrorRequestsTotal(Executor):
    metric: Counter
    counted: bool = False

    def error_execute(self, data: ErrorData) -> None:
        self.metric.labels(data.method, data.path, data.status_code).inc()
        self.counted = True

    def after_execute(self, data: AfterData) -> None:
        if not self.counted and data.status_code >= 500:
            self.metric.labels(data.method, data.path, data.status_code).inc()
        self.counted = False


class CpuPercent(Executor):
    metric: Gauge

    def __init__(self, saturation: Saturation) -> None:
        self.saturation = saturation

    def after_execute(self, data: AfterData) -> None:
        cpu_percent = self.saturation.cpu_percent
        self.metric.set(cpu_percent)


class MemoryPercent(Executor):
    metric: Gauge

    def __init__(self, saturation: Saturation) -> None:
        self.saturation = saturation

    def after_execute(self, data: AfterData) -> None:
        cpu_percent = self.saturation.memory_percent
        self.metric.set(cpu_percent)


GOLDEN_SIGNALS = (
    MetricConfig(
        name="requests_total",
        description="Total HTTP requests",
        labels=["method", "endpoint", "status"],
        executor=RequestTotal(),
    ),
    MetricConfig(
        name="request_duration_seconds",
        description="Request latency in seconds",
        labels=["method", "endpoint", "status"],
        buckets=[0.01, 0.05, 0.1, 0.5, 1.0],
        executor=RequestDurationSeconds(),
    ),
    MetricConfig(
        name="errors_total",
        description="Total HTTP Errors",
        labels=["method", "endpoint", "status"],
        executor=ErrorRequestsTotal(),
    ),
    MetricConfig(
        name="active_requests_total",
        description="Current active requests in application",
        labels=["method", "endpoint"],
        executor=ActiveRequestsTotal(),
    ),
    MetricConfig(
        name="cpu_percent", description="CPU Percent", executor=CpuPercent(saturation_collector)
    ),
    MetricConfig(
        name="memory_percent",
        description="Memory Percent",
        executor=MemoryPercent(saturation_collector),
    ),
)
