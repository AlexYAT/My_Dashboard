"""
Модуль Финансовый трекер для Personal Dashboard.
"""

try:
    from src.core.base_module import BaseModule
except ImportError:
    from core.base_module import BaseModule

from PySide6.QtWidgets import QWidget

from .finance_widget import FinanceWidget


class FinanceModule(BaseModule):
    """Модуль финансового трекера."""

    def __init__(self):
        super().__init__()
        self._module_id = "finance"
        self._version = "0.1.0"
        self._author = "Personal Dashboard"
        self._description = "Трекер доходов и расходов"
        self._requires_confirmation = True
        self._widget: QWidget | None = None

    def get_name(self) -> str:
        return "💰 Финансовый трекер"

    def get_icon(self) -> str:
        return "💰"

    def get_short_name(self) -> str:
        return "Финансы"

    def get_widget(self) -> QWidget:
        if self._widget is None:
            self._widget = FinanceWidget()
        return self._widget

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self._widget = None
