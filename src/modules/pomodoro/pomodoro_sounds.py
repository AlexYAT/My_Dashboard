"""
Звуковые уведомления: QSoundEffect, WAV-файлы (генерируются тонами при первом запуске).
"""

import math
import struct
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect


def _sounds_dir() -> Path:
    from PySide6.QtCore import QStandardPaths
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    folder = Path(loc) / "Personal_Dashboard" / "Pomodoro" / "sounds"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _generate_wav(file_path: Path, frequency: float = 880, duration_ms: int = 200, volume: float = 0.5) -> None:
    """Генерирует простой WAV-файл (моно, 44100 Hz, 16 bit)."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    max_amplitude = 32767 * volume
    with open(file_path, "wb") as f:
        # WAV header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + n_samples * 2))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", n_samples * 2))
        for i in range(n_samples):
            t = i / sample_rate
            sample = max_amplitude * math.sin(2 * math.pi * frequency * t) * (1 - i / n_samples)
            f.write(struct.pack("<h", int(sample)))


def _ensure_sounds() -> dict[str, Path]:
    d = _sounds_dir()
    names = {
        "start_work": (880, 150),
        "end_work": (660, 300),
        "start_break": (523, 150),
        "end_break": (440, 200),
    }
    paths = {}
    for key, (freq, dur) in names.items():
        p = d / f"{key}.wav"
        if not p.exists():
            _generate_wav(p, frequency=freq, duration_ms=dur)
        paths[key] = p
    return paths


class PomodoroSounds:
    """Воспроизведение звуков событий Pomodoro."""

    def __init__(self):
        self._paths = _ensure_sounds()
        self._effects: dict[str, QSoundEffect] = {}
        self._volume = 0.7
        self._enabled = True

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        for e in self._effects.values():
            e.setVolume(self._volume)

    def _play(self, key: str) -> None:
        if not self._enabled or key not in self._paths:
            return
        path = self._paths[key]
        if key not in self._effects:
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(str(path)))
            effect.setVolume(self._volume)
            self._effects[key] = effect
        self._effects[key].play()

    def play_start_work(self) -> None:
        self._play("start_work")

    def play_end_work(self) -> None:
        self._play("end_work")

    def play_start_break(self) -> None:
        self._play("start_break")

    def play_end_break(self) -> None:
        self._play("end_break")
