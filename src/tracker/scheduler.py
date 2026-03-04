import threading
from datetime import datetime, timedelta, timezone

from .service import run_tracking


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class TrackingScheduler:
    def __init__(
        self,
        api_key: str,
        csv_path: str,
        urls_file: str,
        sleep_seconds: float,
        history_json_path: str,
    ):
        self.api_key = api_key
        self.csv_path = csv_path
        self.urls_file = urls_file
        self.sleep_seconds = sleep_seconds
        self.history_json_path = history_json_path

        self._interval_seconds = 0.0
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._last_run_at = None
        self._next_run_at = None
        self._last_result = None
        self._last_error = None

    def start(self, interval_seconds: float) -> bool:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be > 0")

        with self._lock:
            if self.is_running():
                return False
            self._interval_seconds = float(interval_seconds)
            self._stop_event.clear()
            self._last_error = None
            self._next_run_at = _utc_now_iso()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return True

    def stop(self) -> bool:
        with self._lock:
            running = self.is_running()
            thread = self._thread
            self._stop_event.set()

        if thread and running:
            thread.join(timeout=10)

        with self._lock:
            self._next_run_at = None
        return running

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> dict:
        with self._lock:
            return {
                "running": self.is_running(),
                "interval_seconds": self._interval_seconds,
                "last_run_at": self._last_run_at,
                "next_run_at": self._next_run_at,
                "last_result": self._last_result,
                "last_error": self._last_error,
            }

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                self._last_run_at = _utc_now_iso()
                self._last_error = None

            try:
                result = run_tracking(
                    api_key=self.api_key,
                    csv_path=self.csv_path,
                    urls_file=self.urls_file,
                    sleep_seconds=self.sleep_seconds,
                    history_json_path=self.history_json_path,
                )
                with self._lock:
                    self._last_result = result
            except Exception as exc:
                with self._lock:
                    self._last_error = str(exc)

            next_run = datetime.now(timezone.utc) + timedelta(seconds=self._interval_seconds)
            with self._lock:
                self._next_run_at = next_run.replace(microsecond=0).isoformat()

            if self._stop_event.wait(self._interval_seconds):
                break

        with self._lock:
            self._next_run_at = None
