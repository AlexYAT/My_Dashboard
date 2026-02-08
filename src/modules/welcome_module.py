"""
Пример модуля дашборда — приветственный блок.
Используется для проверки загрузки через ModuleManager и регистрации в DashboardApp.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

# Импорт при динамической загрузке: проект должен быть запущен из корня (см. main.py)
try:
    from src.core.base_module import BaseModule
except ImportError:
    from core.base_module import BaseModule


class WelcomeModule(BaseModule):
    """Модуль с приветствием."""

    def __init__(self):
        super().__init__()
        self._module_id = "welcome"
        self._version = "0.1.0"
        self._author = "Personal Dashboard"
        self._description = "Приветственный блок дашборда"
        self._widget: QWidget | None = None

    def get_name(self) -> str:
        return "Приветствие"

    def get_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = QLabel("Добро пожаловать в Personal Dashboard!")
            self._widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._widget.setStyleSheet("font-size: 16px; padding: 20px;")
        return self._widget

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self._widget = None
