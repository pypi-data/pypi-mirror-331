from unittest.mock import Mock

import pytest
from prometheus_client import Counter, Gauge, Histogram, Summary

from fast_prometheus.executor import Executor
from fast_prometheus.factory import MetricFactory


def create_config(tp_metric, name, extra_params={}) -> Mock:
    mock_config = Mock()
    executor = Mock(spec=Executor)
    executor.__annotations__ = {"metric": tp_metric}
    mock_config.executor = executor
    mock_config.description = "test_description"
    mock_config.labels = ["test_path", "test_status"]
    for name, value in extra_params.items():
        setattr(mock_config, name, value)
    return mock_config


@pytest.mark.parametrize(
    "name,tp_metric",
    [("test_total", Counter), ("app_test_sum", Summary), ("app_test_percent", Gauge)],
)
def test_factory_get_success(name, tp_metric) -> None:
    config = create_config(tp_metric, name)
    factory = MetricFactory()
    metric = factory.get(config, name)
    name = "test" if name == "test_total" else name
    assert isinstance(metric, tp_metric)
    assert metric._name == name
    assert metric._documentation == "test_description"
    assert metric._labelnames == ("test_path", "test_status")


@pytest.mark.parametrize(
    "name,tp_metric,extra_params",
    [("app_test_seconds", Histogram, {"buckets": [0.01, 0.05, 0.1, 0.5, 1.0]})],
)
def test_factory_get_extra_params_success(tp_metric, name, extra_params) -> None:
    config = create_config(tp_metric, name, extra_params)
    factory = MetricFactory()
    metric = factory.get(config, name)
    assert isinstance(metric, Histogram)
    assert metric._name == "app_test_seconds"
    assert metric._documentation == "test_description"
    assert metric._labelnames == ("test_path", "test_status")
    assert metric._kwargs["buckets"] == [0.01, 0.05, 0.1, 0.5, 1.0]
