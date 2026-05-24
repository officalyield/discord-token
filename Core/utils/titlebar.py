import ctypes
import threading
import time
import sys
from typing import Callable


class TitleBarUpdater:
    def __init__(self, stats_provider: Callable[[], str], interval: float = 0.5):
        self.stats_provider = stats_provider
        self.interval = interval

        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="TitleBarUpdater",
                daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                title = self.stats_provider()
                if title:
                    self._set_title(title)
            except Exception:
                pass

            time.sleep(self.interval)

    @staticmethod
    def _set_title(title: str) -> None:
        if sys.platform == "win32":
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        else:
            sys.stdout.write(f"\33]0;{title}\a")
            sys.stdout.flush()
