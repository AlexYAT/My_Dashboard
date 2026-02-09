"""
Круговая диаграмма прогресса таймера Pomodoro.
Отрисовка QPainter: полный круг = интервал, заполненный сегмент = прошедшее время.
Цвета: работа (зелёный→оранжевый→красный), перерыв (синий→голубой).
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QConicalGradient
from PySide6.QtWidgets import QWidget


class CircularProgressWidget(QWidget):
    """Виджет круговой диаграммы прогресса (прошедшее/оставшееся время)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._total_seconds = 25 * 60
        self._elapsed_seconds = 0.0
        self._is_work_mode = True
        self._is_paused = False

    def set_progress(self, total_seconds: int, elapsed_seconds: float) -> None:
        self._total_seconds = max(1, total_seconds)
        self._elapsed_seconds = max(0.0, min(elapsed_seconds, self._total_seconds))
        self.update()

    def set_work_mode(self, work: bool) -> None:
        self._is_work_mode = work
        self.update()

    def set_paused(self, paused: bool) -> None:
        self._is_paused = paused
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._total_seconds <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        side = min(w, h)
        margin = 12
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        # Фоновый круг (оставшееся время)
        bg_color = QColor(60, 60, 60)
        painter.setPen(QPen(bg_color, 14, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 90 * 16, 360 * 16)

        # Прогресс (прошедшее время), старт с верха (12 часов)
        progress = self._elapsed_seconds / self._total_seconds
        span = int(360 * 16 * progress)

        if span <= 0:
            return

        if self._is_paused:
            pen_color = QColor(255, 193, 7)
            painter.setPen(QPen(pen_color, 14, Qt.PenStyle.SolidLine))
        elif self._is_work_mode:
            # Работа: градиент зелёный → оранжевый → красный по прогрессу
            gradient = QConicalGradient(rect.center(), 90)
            gradient.setColorAt(0.0, QColor(76, 175, 80))
            gradient.setColorAt(0.5, QColor(255, 152, 0))
            gradient.setColorAt(1.0, QColor(244, 67, 54))
            painter.setPen(QPen(QBrush(gradient), 14, Qt.PenStyle.SolidLine))
        else:
            # Перерыв: синий → голубой
            gradient = QConicalGradient(rect.center(), 90)
            gradient.setColorAt(0.0, QColor(33, 150, 243))
            gradient.setColorAt(1.0, QColor(0, 188, 212))
            painter.setPen(QPen(QBrush(gradient), 14, Qt.PenStyle.SolidLine))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 90 * 16, -span)

        painter.end()
