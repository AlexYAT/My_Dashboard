"""
Настройки Pomodoro: время работы/перерывов, помидоров до длинного перерыва.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json


WORK_OPTIONS = (20 * 60, 25 * 60, 30 * 60)
SHORT_BREAK_OPTIONS = (3 * 60, 5 * 60, 10 * 60)
LONG_BREAK_OPTIONS = (15 * 60, 20 * 60, 25 * 60, 30 * 60)
DEFAULT_TOMATOES_UNTIL_LONG = 4


@dataclass
class PomodoroSettings:
    """Настройки интервалов и счётчика сессий."""

    work_seconds: int = 25 * 60
    short_break_seconds: int = 5 * 60
    long_break_seconds: int = 15 * 60
    tomatoes_until_long_break: int = 4
    sound_enabled: bool = True
    sound_volume: float = 0.7

    def validate(self) -> None:
        if self.work_seconds not in WORK_OPTIONS:
            self.work_seconds = 25 * 60
        if self.short_break_seconds not in SHORT_BREAK_OPTIONS:
            self.short_break_seconds = 5 * 60
        if self.long_break_seconds not in LONG_BREAK_OPTIONS:
            self.long_break_seconds = 15 * 60
        self.tomatoes_until_long_break = max(1, min(10, self.tomatoes_until_long_break))
        self.sound_volume = max(0.0, min(1.0, self.sound_volume))

    def to_dict(self) -> dict:
        return {
            "work_seconds": self.work_seconds,
            "short_break_seconds": self.short_break_seconds,
            "long_break_seconds": self.long_break_seconds,
            "tomatoes_until_long_break": self.tomatoes_until_long_break,
            "sound_enabled": self.sound_enabled,
            "sound_volume": self.sound_volume,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PomodoroSettings":
        s = cls(
            work_seconds=data.get("work_seconds", 25 * 60),
            short_break_seconds=data.get("short_break_seconds", 5 * 60),
            long_break_seconds=data.get("long_break_seconds", 15 * 60),
            tomatoes_until_long_break=data.get("tomatoes_until_long_break", 4),
            sound_enabled=data.get("sound_enabled", True),
            sound_volume=data.get("sound_volume", 0.7),
        )
        s.validate()
        return s


def _config_path() -> Path:
    from PySide6.QtCore import QStandardPaths
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    folder = Path(loc) / "Personal_Dashboard" / "Pomodoro"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


def load_settings() -> PomodoroSettings:
    p = _config_path()
    if not p.exists():
        return PomodoroSettings()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return PomodoroSettings.from_dict(data)
    except Exception:
        return PomodoroSettings()


def save_settings(settings: PomodoroSettings) -> None:
    p = _config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
