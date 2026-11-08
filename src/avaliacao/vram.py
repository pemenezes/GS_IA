"""Amostragem da VRAM usada na GPU 0 (pico durante um bloco `with`)."""

from __future__ import annotations

import threading
import time

import pynvml


class MonitorVRAM:
    def __init__(self, intervalo: float = 0.1) -> None:
        pynvml.nvmlInit()
        self.h = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.intervalo = intervalo
        self.pico = 0
        self._parar = threading.Event()
        self._thread: threading.Thread | None = None

    def usada_mib(self) -> int:
        return pynvml.nvmlDeviceGetMemoryInfo(self.h).used // 2**20

    def __enter__(self) -> MonitorVRAM:
        self.pico = self.usada_mib()
        self._parar.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def _loop(self) -> None:
        while not self._parar.is_set():
            self.pico = max(self.pico, self.usada_mib())
            time.sleep(self.intervalo)

    def __exit__(self, *_: object) -> None:
        self._parar.set()
        if self._thread:
            self._thread.join()
