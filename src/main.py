"""
Personal Dashboard — точка входа.
Создаёт экземпляр DashboardApp и подключает модули.
"""

import sys
from pathlib import Path

# Корень проекта в path для импорта src.* при запуске python src/main.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from src.core import DashboardApp


def main():
    app = QApplication(sys.argv)

    # Создаём главное окно приложения
    window = DashboardApp(title="Personal Dashboard", version="0.1")

    # Загрузка модулей через ModuleManager
    manager = window.get_module_manager()
    welcome = manager.load_module("welcome_module")
    if welcome is not None:
        window.register_module(welcome)
    pomodoro = manager.load_module("pomodoro")
    if pomodoro is not None:
        window.register_module(pomodoro)

    # Альтернатива: создать модуль и зарегистрировать:
    # from src.modules.welcome_module import WelcomeModule
    # window.register_module(WelcomeModule())

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
