from collections.abc import Sequence

from fast_prometheus.config import MetricConfig
from fast_prometheus.exceptions import NameAlreadyExistsError
from fast_prometheus.executor import AfterData, BeforeData, ErrorData, Executor
from fast_prometheus.factory import MetricFactory
from fast_prometheus.golden_signals import GOLDEN_SIGNALS
from fast_prometheus.types import NameMetric


class ExecutorRegistry:
    __slots__ = ("_executors", "_factory", "_names", "app_name")

    def __init__(self, app_name: str) -> None:
        self.app_name = app_name
        self._executors: list[Executor] = []
        self._names: set[NameMetric] = set()
        self._factory = MetricFactory()

    def add(self, config: MetricConfig) -> None:
        full_name = f"{self.app_name}_{config.name}"
        self._check_name(full_name)
        metric = self._factory.get(config, full_name)
        executor = config.executor
        executor.metric = metric  # type: ignore
        self._executors.append(executor)
        self._names.add(full_name)

    def add_all(self, configs: Sequence[MetricConfig]) -> None:
        for config in configs:
            self.add(config)

    def init_golden_signals(self) -> None:
        self.add_all(GOLDEN_SIGNALS)

    def _check_name(self, name: NameMetric) -> None:
        if name in self._names:
            raise NameAlreadyExistsError(f"Metric {name} registered in {self.__class__.__name__}")

    async def before_execute(self, data: BeforeData) -> None:
        for executor in self._executors:
            executor.before_execute(data)

    async def after_execute(self, data: AfterData) -> None:
        for executor in self._executors:
            executor.after_execute(data)

    async def error_execute(self, data: ErrorData) -> None:
        for executor in self._executors:
            executor.error_execute(data)
