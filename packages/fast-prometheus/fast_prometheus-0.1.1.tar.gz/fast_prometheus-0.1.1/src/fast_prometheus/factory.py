from collections.abc import Sequence

from prometheus_client.metrics import Histogram

from fast_prometheus.config import MetricConfig
from fast_prometheus.types import MetricImpl

_EXTRA_REQUIRED_PARAMS: dict[type[MetricImpl], list[str]] = {Histogram: ["buckets"]}


class MetricFactory:
    __slots__ = ()

    def get(self, config: MetricConfig, full_name_metric: str) -> MetricImpl:
        metric_type = config.executor.__annotations__["metric"]
        extra_params = _EXTRA_REQUIRED_PARAMS.get(metric_type)
        return metric_type(**self._get_params(config, full_name_metric, extra_params))  # type: ignore

    def _get_params(
        self, config: MetricConfig, full_name_metric: str, extra_params: list[str] | None = None
    ) -> dict[str, Sequence[str]]:
        params = {
            "name": full_name_metric,
            "documentation": config.description,
            "labelnames": config.labels or [],
        }
        if extra_params:
            for param in extra_params:
                value = getattr(config, param)
                if value:
                    params[param] = value
        return params
