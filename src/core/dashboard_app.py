"""
Главный класс приложения Personal Dashboard.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .base_module import BaseModule
from .module_manager import ModuleManager


class DashboardApp(QMainWindow):
    """Главное окно приложения с центральным виджетом для модулей и системным меню."""

    def __init__(
        self,
        title: str = "Personal Dashboard",
        version: str = "0.1",
        modules_path: Optional[Path] = None,
    ):
        super().__init__()
        self.setWindowTitle(f"{title} v{version}")
        self.setMinimumSize(400, 300)
        self.resize(800, 600)

        self._module_manager = ModuleManager(modules_path)
        self._central_container: Optional[QWidget] = None
        self._central_layout: Optional[QVBoxLayout] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Настраивает интерфейс: центральный виджет и меню."""
        # Центральный виджет для размещения модулей
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        self._central_container = container
        self._central_layout = QVBoxLayout(container)
        self._central_layout.setContentsMargins(16, 16, 16, 16)
        self._central_layout.setSpacing(12)
        self._central_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Системное меню: Файл → Выход
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

    def register_module(self, module: BaseModule) -> None:
        """Регистрирует модуль и добавляет его виджет в центральную область."""
        if self._central_layout is None:
            return
        widget = module.get_widget()
        if widget is not None:
            self._central_layout.addWidget(widget)

    def get_module_manager(self) -> ModuleManager:
        """Возвращает менеджер модулей для загрузки модулей из папки modules/."""
        return self._module_manager
