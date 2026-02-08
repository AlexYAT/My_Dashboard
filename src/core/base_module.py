"""
Базовый класс для модулей Personal Dashboard.
Все модули должны наследовать BaseModule и реализовать обязательные методы.
"""

from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget


class BaseModule(ABC):
    """Абстрактный базовый класс для модулей дашборда."""

    def __init__(self):
        self._module_id: str = ""
        self._version: str = "0.1.0"
        self._author: str = ""
        self._description: str = ""

    @property
    def module_id(self) -> str:
        """Уникальный идентификатор модуля."""
        return self._module_id

    @property
    def version(self) -> str:
        """Версия модуля."""
        return self._version

    @property
    def author(self) -> str:
        """Автор модуля."""
        return self._author

    @property
    def description(self) -> str:
        """Описание модуля."""
        return self._description

    @abstractmethod
    def get_name(self) -> str:
        """Возвращает отображаемое имя модуля."""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Возвращает виджет модуля для отображения в дашборде."""
        pass

    @abstractmethod
    def on_load(self) -> None:
        """Вызывается при загрузке модуля в приложение."""
        pass

    @abstractmethod
    def on_unload(self) -> None:
        """Вызывается при выгрузке модуля из приложения."""
        pass
