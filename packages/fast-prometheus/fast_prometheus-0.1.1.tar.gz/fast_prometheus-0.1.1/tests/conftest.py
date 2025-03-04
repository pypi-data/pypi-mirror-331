from collections.abc import Generator

import pytest
from prometheus_client import REGISTRY


@pytest.fixture(autouse=True)
def cleanup_registry() -> Generator[None]:
    yield
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
