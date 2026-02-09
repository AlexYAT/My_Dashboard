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

    # Главное окно: панель модулей слева, активный модуль по клику
    window = DashboardApp(title="Personal Dashboard", version="0.1")
    # Модули загружаются лениво при нажатии на кнопку в панели.
    # Последний открытый модуль восстанавливается из конфига при следующем запуске.

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
