"""
Personal Dashboard - главный модуль приложения.
Запускает окно PySide6 с приветствием.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Dashboard v0.1")
        self.setMinimumSize(400, 300)
        self.resize(600, 400)

        label = QLabel("Добро пожаловать в Personal Dashboard!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; padding: 20px;")
        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
