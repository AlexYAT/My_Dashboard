"""
Модуль Pomodoro для Personal Dashboard.
Таймер по технике 25 минут работы / 5 минут перерыва.
"""

try:
    from src.core.base_module import BaseModule
except ImportError:
    from core.base_module import BaseModule

from PySide6.QtWidgets import QWidget

from .pomodoro_widget import PomodoroWidget


class PomodoroModule(BaseModule):
    """Модуль таймера Pomodoro (25 мин работа, 5 мин перерыв)."""

    def __init__(self):
        super().__init__()
        self._module_id = "pomodoro"
        self._version = "0.1.0"
        self._author = "Personal Dashboard"
        self._description = "Таймер Pomodoro: 25 минут работы, 5 минут перерыва"
        self._requires_confirmation = True
        self._widget: QWidget | None = None

    def get_name(self) -> str:
        return "🍅 Pomodoro Timer"

    def get_icon(self) -> str:
        return "🍅"

    def get_short_name(self) -> str:
        return "Pomodoro"

    def get_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = PomodoroWidget()
        return self._widget

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self._widget = None
