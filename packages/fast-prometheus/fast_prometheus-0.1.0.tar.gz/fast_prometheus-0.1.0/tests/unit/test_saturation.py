from fast_prometheus.saturation import Saturation


def test_saturation_collector() -> None:
    saturation = Saturation()
    assert saturation.cpu_percent == 0.0
    assert saturation.memory_percent == 0.0
    assert saturation._running is True
    del saturation
