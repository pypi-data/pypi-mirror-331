# type: ignore
import pytest
from prometheus_client import CollectorRegistry, Counter

from fast_prometheus.config import MetricConfig
from fast_prometheus.exceptions import ConfigAttributeError
from fast_prometheus.executor import Executor


class ValidExecutor(Executor):
    metric: Counter


class ValidRegistry(CollectorRegistry):
    pass


class InvalidExecutor:
    pass


class ExecutorWithoutMetric(Executor):
    x: int


class ExecutorWithInvalidMetric(Executor):
    metric: str


class TestMetricConfigValidation:
    def test_valid_config(self) -> None:
        assert MetricConfig(
            name="test_metric",
            description="Test description",
            executor=ValidExecutor(),
            labels=["label1", "label2"],
            buckets=[0.1, 0.5, 0.9],
            static_labels=[{"label1": 1}, {"label2": 2}],
            collector_registry=ValidRegistry(),
        )


class TestRequiredFields:
    def test_missing_name(self) -> None:
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(name=None, description="desc", executor=ValidExecutor())
        assert "Field 'name' must not be None" in str(exc.value)

    def test_missing_description(self) -> None:
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(name="name", description=None, executor=ValidExecutor())
        assert "Field 'description' must not be None" in str(exc.value)

    def test_missing_executor(self) -> None:
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(name="name", description="desc", executor=None)
        assert "Field 'executor' must not be None" in str(exc.value)


class TestListValidation:
    @pytest.mark.parametrize(
        "field,value,element_type",
        [
            ("labels", "test", str),
            ("buckets", ("test_tuple",), float),
            ("static_labels", {"test_dict": "test"}, dict),
        ],
    )
    def test_not_a_list(self, field, value, element_type):
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(
                name="test", description="test", executor=ValidExecutor(), **{field: value}
            )
        assert "must be a list" in str(exc.value)

    @pytest.mark.parametrize(
        "field,bad_value,element_type",
        [
            ("labels", [123, 456], str),
            ("buckets", ["test"], float),
            ("static_labels", ["test"], dict),
        ],
    )
    def test_invalid_list_elements(self, field, bad_value, element_type) -> None:
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(
                name="test", description="test", executor=ValidExecutor(), **{field: bad_value}
            )
        assert f"must be of type {element_type.__name__}" in str(exc.value)


class TestExecutorValidation:
    @pytest.mark.parametrize(
        "executor_class,expected_error",
        [
            (InvalidExecutor(), "must be of type Executor"),
            (ExecutorWithoutMetric(), "must have a 'metric' class variable"),
            (ExecutorWithInvalidMetric(), "must be a subclass of MetricImpl"),
        ],
    )
    def test_invalid_executors(self, executor_class, expected_error) -> None:
        with pytest.raises(ConfigAttributeError) as exc:
            MetricConfig(name="test", description="test", executor=executor_class)
        assert expected_error in str(exc.value)
