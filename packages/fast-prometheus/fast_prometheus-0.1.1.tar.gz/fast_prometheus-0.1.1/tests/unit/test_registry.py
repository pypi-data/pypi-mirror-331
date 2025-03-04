from unittest.mock import Mock

import pytest
from prometheus_client import Histogram

from fast_prometheus import (
    Executor,
    ExecutorRegistry,
    MetricConfig,
)
from fast_prometheus.exceptions import NameAlreadyExistsError
from fast_prometheus.factory import MetricFactory


def test_init_registry() -> None:
    registry = ExecutorRegistry("app")
    assert registry.app_name == "app"
    assert len(registry._executors) == 0
    assert len(registry._names) == 0
    assert isinstance(registry._factory, MetricFactory)


def test_init_golden_signals() -> None:
    registry = ExecutorRegistry("app")
    registry.init_golden_signals()
    assert len(registry._executors) == 6
    assert len(registry._names) == 6
    assert isinstance(registry._executors[0], Executor)


def test_check_name() -> None:
    registry = ExecutorRegistry("app")
    executor = Mock(spec=Executor)
    executor.__annotations__ = {"metric": Histogram}

    registry.add(MetricConfig(name="test_total", description="test_description", executor=executor))
    with pytest.raises(NameAlreadyExistsError) as exc:
        registry.add(
            MetricConfig(name="test_total", description="test_description", executor=executor)
        )
    assert "Metric app_test_total registered in" in str(exc.value)
