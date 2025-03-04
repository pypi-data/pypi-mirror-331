from dataclasses import dataclass

from prometheus_client import REGISTRY, CollectorRegistry

from fast_prometheus.exceptions import ConfigAttributeError
from fast_prometheus.executor import Executor
from fast_prometheus.types import MetricImpl


@dataclass(slots=True)
class MetricConfig:
    name: str
    description: str
    executor: Executor
    labels: list[str] | None = None
    buckets: list[float] | None = None
    static_labels: list[dict] | None = None
    collector_registry: CollectorRegistry = REGISTRY

    def __post_init__(self) -> None:
        self._validate_not_none(["name", "description", "executor"])
        self._validate_type("name", str)
        self._validate_type("description", str)
        self._validate_type("executor", Executor)
        self._validate_type("collector_registry", CollectorRegistry)
        self._validate_list("labels", str)
        self._validate_list("buckets", float)
        self._validate_list("static_labels", dict)
        self._validate_executor()

    def _validate_executor(self) -> None:
        if "metric" not in self.executor.__annotations__:
            raise ConfigAttributeError("Executor must have a 'metric' class variable annotation")
        metric_class = self.executor.__annotations__["metric"]
        if not (isinstance(metric_class, type) and issubclass(metric_class, MetricImpl)):
            raise ConfigAttributeError(
                f"Executor's 'metric' must be a subclass of MetricImpl, got {metric_class}"
            )

    def _validate_type(self, field_name: str, expected_type: type) -> None:
        value = getattr(self, field_name)
        if not isinstance(value, expected_type):
            raise ConfigAttributeError(
                f"Field '{field_name}' must be of type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    def _validate_list(self, field_name: str, element_type: type) -> None:
        value = getattr(self, field_name)
        if value is None:
            return
        if not isinstance(value, list):
            raise ConfigAttributeError(
                f"Field '{field_name}' must be a list, got {type(value).__name__}"
            )
        for idx, item in enumerate(value):
            if not isinstance(item, element_type):
                raise ConfigAttributeError(
                    f"Field '{field_name}[{idx}]' must be of type {element_type.__name__}, "
                    f"got {type(item).__name__}"
                )

    def _validate_not_none(self, fields_names: list[str]) -> None:
        for name in fields_names:
            value = getattr(self, name)
            if value is None:
                raise ConfigAttributeError(f"Field '{name}' must not be None")
