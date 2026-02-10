"""
Главный виджет модуля Финансовый трекер.
Пока — заглушка с текстом «в разработке».
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class FinanceWidget(QWidget):
    """Виджет финансового трекера (заглушка)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("financeWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        label = QLabel("Финансовый трекер (в разработке)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; padding: 20px; color: #e0e0e0;")
        label.setObjectName("financePlaceholder")
        layout.addWidget(label)
        self.setMinimumWidth(320)
