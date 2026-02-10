"""
Главный класс приложения Personal Dashboard.
Панель навигации с кнопками модулей, QStackedWidget для активного модуля,
сохранение последнего модуля в JSON.
"""

import json
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from .base_module import BaseModule
from .module_manager import ModuleManager


def _config_path() -> Path:
    from PySide6.QtCore import QStandardPaths
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    folder = Path(loc) / "Personal_Dashboard"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "dashboard_state.json"


class DashboardApp(QMainWindow):
    """Главное окно: панель навигации слева, центральная область — активный модуль (QStackedWidget)."""

    def __init__(
        self,
        title: str = "Personal Dashboard",
        version: str = "0.1",
        modules_path: Optional[Path] = None,
    ):
        super().__init__()
        self._app_title = title
        self._app_version = version
        self.setWindowTitle(f"{title} v{version}")
        self.setMinimumSize(600, 400)
        self.resize(900, 600)

        self._module_manager = ModuleManager(modules_path)
        self._stacked = QStackedWidget()
        self._module_name_to_index: dict[str, int] = {}
        self._nav_buttons: list[tuple[str, QPushButton]] = []
        self._current_module_name: Optional[str] = None
        self._config_file = _config_path()

        self.setup_ui()
        self._restore_last_module()

    def setup_ui(self) -> None:
        """Панель навигации слева + QStackedWidget по центру + меню."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Панель навигации слева
        nav_panel = self._create_nav_panel()
        content_layout.addWidget(nav_panel)

        # Центральная область: QStackedWidget
        self._stacked.setObjectName("stackedWidget")
        self._stacked.setMinimumWidth(400)
        content_layout.addWidget(self._stacked, 1)

        main_layout.addWidget(content)

        # Меню: Файл → Выход
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self._on_quit)
        file_menu.addAction(exit_action)

        self._apply_global_styles()

    def _create_nav_panel(self) -> QWidget:
        """Панель навигации с кнопками модулей (слева по вертикали)."""
        panel = QFrame()
        panel.setObjectName("navPanel")
        panel.setFixedWidth(180)
        panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)

        for module_name in self._module_manager.get_available_modules():
            btn = QPushButton(self._display_name_for_module_file(module_name))
            btn.setObjectName("navButton")
            btn.setProperty("moduleName", module_name)
            btn.setProperty("active", False)
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.clicked.connect(lambda checked=False, n=module_name: self._on_nav_click(n))
            layout.addWidget(btn)
            self._nav_buttons.append((module_name, btn))

        layout.addStretch()
        return panel

    def _display_name_for_module_file(self, module_name: str) -> str:
        """Отображаемое имя до загрузки модуля (по имени файла)."""
        if module_name == "welcome_module":
            return "👋 Привет"
        if module_name == "pomodoro":
            return "🍅 Pomodoro"
        if module_name == "finance":
            return "💰 Финансы"
        return module_name.replace("_", " ").title()

    def _on_nav_click(self, module_name: str) -> None:
        """Загрузить модуль (если ещё не загружен), переключить стек, обновить заголовок и подсветку."""
        if module_name in self._module_name_to_index:
            idx = self._module_name_to_index[module_name]
            self._stacked.setCurrentIndex(idx)
        else:
            mod = self._module_manager.load_module(module_name)
            if mod is None:
                return
            widget = mod.get_widget()
            if widget is None:
                return
            idx = self._stacked.addWidget(widget)
            self._module_name_to_index[module_name] = idx
            self._stacked.setCurrentIndex(idx)
            # Обновить кнопку: иконка + короткое имя
            for name, btn in self._nav_buttons:
                if name == module_name:
                    icon = mod.get_icon()
                    short = mod.get_short_name()
                    btn.setText(f"{icon} {short}".strip() if icon else short)
                    break

        self._current_module_name = module_name
        mod = self._module_manager.load_module(module_name)
        if mod is not None:
            self.setWindowTitle(f"{self._app_title} v{self._app_version} — {mod.get_name()}")
        self._save_last_module(module_name)
        self._update_nav_active(module_name)

        # Плавное появление (опционально)
        self._stacked.currentWidget().setGraphicsEffect(None)

    def _update_nav_active(self, active_name: str) -> None:
        for name, btn in self._nav_buttons:
            btn.setProperty("active", name == active_name)
            btn.setChecked(name == active_name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _apply_global_styles(self) -> None:
        self.setStyleSheet("""
            #navPanel {
                background-color: #252526;
                border-right: 1px solid #3c3c3c;
            }
            #navButton {
                text-align: left;
                padding: 10px 12px;
                border: none;
                border-radius: 6px;
                background: transparent;
                color: #cccccc;
                font-size: 13px;
            }
            #navButton:hover {
                background-color: #2a2d2e;
                color: #ffffff;
            }
            #navButton[active="true"] {
                background-color: #094771;
                color: #ffffff;
            }
            #stackedWidget {
                background-color: #1e1e1e;
            }
        """)

    def _save_last_module(self, module_name: str) -> None:
        try:
            data = {"last_module": module_name}
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            self._config_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _restore_last_module(self) -> None:
        try:
            if not self._config_file.exists():
                self._open_first_available()
                return
            data = json.loads(self._config_file.read_text(encoding="utf-8"))
            last = data.get("last_module")
            if last and last in [n for n, _ in self._nav_buttons]:
                self._on_nav_click(last)
                return
        except Exception:
            pass
        self._open_first_available()

    def _open_first_available(self) -> None:
        """Открыть первый доступный модуль (Welcome или первый в списке)."""
        preferred = "welcome_module" if "welcome_module" in self._module_manager.get_available_modules() else None
        names = self._module_manager.get_available_modules()
        to_open = preferred if preferred and preferred in names else (names[0] if names else None)
        if to_open:
            self._on_nav_click(to_open)
        else:
            self.setWindowTitle(f"{self._app_title} v{self._app_version}")

    def _on_quit(self) -> None:
        if self._current_module_name:
            mod = self._module_manager.load_module(self._current_module_name)
            if mod is not None and getattr(mod, "requires_confirmation", False) and mod.requires_confirmation:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    "Модуль может иметь несохранённые данные. Выйти?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        QApplication.quit()

    def register_module(self, module: BaseModule) -> None:
        """Устаревший метод: модули теперь открываются по кнопке. Оставлен для совместимости."""
        pass

    def get_module_manager(self) -> ModuleManager:
        return self._module_manager
