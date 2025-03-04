import time
from threading import Thread

import psutil


class Saturation:
    __slots__ = ("_running", "cpu_percent", "memory_percent")

    def __init__(self) -> None:
        self.cpu_percent: float = 0.0
        self.memory_percent: float = 0.0
        self._running = True
        self._start_metric_thread()

    def _start_metric_thread(self) -> None:
        thread = Thread(target=self._update_saturation_metrics_sync, daemon=True)
        thread.start()

    def _update_saturation_metrics_sync(self) -> None:
        while self._running:
            self.cpu_percent = psutil.cpu_percent()
            self.memory_percent = psutil.virtual_memory().percent
            time.sleep(5)

    def __del__(self) -> None:
        self._running = False


saturation_collector = Saturation()
