from typing import TypeAlias

from prometheus_client.metrics import Counter, Gauge, Histogram, Summary

NameMetric: TypeAlias = str
MetricImpl = Histogram | Counter | Gauge | Summary
