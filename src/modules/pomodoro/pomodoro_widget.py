"""
Виджет таймера Pomodoro: работа 25 мин, перерыв 5 мин.
"""

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

WORK_SECONDS = 25 * 60
BREAK_SECONDS = 5 * 60


class PomodoroWidget(QWidget):
    """Виджет с таймером Pomodoro и кнопками управления."""

    timer_finished = Signal()
    mode_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._remaining_seconds = WORK_SECONDS
        self._is_work_mode = True
        self._is_running = False
        self._pomodoro_count = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._setup_ui()
        self._update_display()
        self._apply_mode_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setMinimumWidth(320)
        self.setObjectName("pomodoroWidget")

        # Метка режима
        self._mode_label = QLabel("РЕЖИМ РАБОТЫ")
        self._mode_label.setObjectName("modeLabel")
        self._mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_mode = QFont()
        font_mode.setPointSize(12)
        font_mode.setBold(True)
        self._mode_label.setFont(font_mode)
        layout.addWidget(self._mode_label)

        # Таймер (MM:SS)
        self._time_label = QLabel("25:00")
        self._time_label.setObjectName("timeLabel")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_time = QFont("Consolas", 48, QFont.Weight.Bold)
        self._time_label.setFont(font_time)
        layout.addWidget(self._time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопки
        buttons_layout = QGridLayout()
        self._btn_start = QPushButton("▶ Старт")
        self._btn_start.setObjectName("btnStart")
        self._btn_start.clicked.connect(self._on_start)
        buttons_layout.addWidget(self._btn_start, 0, 0)

        self._btn_pause = QPushButton("⏸ Пауза")
        self._btn_pause.setObjectName("btnPause")
        self._btn_pause.setEnabled(False)
        self._btn_pause.clicked.connect(self._on_pause)
        buttons_layout.addWidget(self._btn_pause, 0, 1)

        self._btn_reset = QPushButton("↻ Сброс")
        self._btn_reset.setObjectName("btnReset")
        self._btn_reset.clicked.connect(self._on_reset)
        buttons_layout.addWidget(self._btn_reset, 1, 0)

        self._btn_break = QPushButton("🔄 Перерыв")
        self._btn_break.setObjectName("btnBreak")
        self._btn_break.clicked.connect(self._on_switch_break)
        buttons_layout.addWidget(self._btn_break, 1, 1)

        layout.addLayout(buttons_layout)

        # Статистика
        self._stats_label = QLabel("Завершено помидоров: 0")
        self._stats_label.setObjectName("statsLabel")
        self._stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._stats_label)

        self._base_styles = self._get_base_styles()
        self._set_styles()

    def _get_base_styles(self) -> str:
        return """
            #pomodoroWidget {
                border-radius: 12px;
                border: 1px solid #404040;
            }
            #modeLabel { }
            #timeLabel {
                color: #ffffff;
                letter-spacing: 4px;
            }
            #btnStart {
                background-color: #2e7d32;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
            }
            #btnStart:hover { background-color: #388e3c; }
            #btnStart:disabled { background-color: #555; color: #999; }
            #btnPause {
                background-color: #c62828;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
            }
            #btnPause:hover { background-color: #d32f2f; }
            #btnPause:disabled { background-color: #555; color: #999; }
            #btnReset {
                background-color: #ef6c00;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
            }
            #btnReset:hover { background-color: #f57c00; }
            #btnBreak {
                background-color: #1565c0;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
            }
            #btnBreak:hover { background-color: #1976d2; }
            #statsLabel { color: #b0b0b0; font-size: 14px; }
        """

    def _set_styles(self) -> None:
        self._apply_mode_style()

    def _apply_mode_style(self) -> None:
        if self._is_work_mode:
            self._mode_label.setText("РЕЖИМ РАБОТЫ")
            mode_style = (
                "#pomodoroWidget { background-color: #1b3d1f; border-color: #2e7d32; }\n"
                "#modeLabel { color: #81c784; }"
            )
        else:
            self._mode_label.setText("РЕЖИМ ОТДЫХА")
            mode_style = (
                "#pomodoroWidget { background-color: #0d2137; border-color: #1565c0; }\n"
                "#modeLabel { color: #64b5f6; }"
            )
        self.setStyleSheet(self._base_styles + mode_style)

    def _update_display(self) -> None:
        m = self._remaining_seconds // 60
        s = self._remaining_seconds % 60
        self._time_label.setText(f"{m:02d}:{s:02d}")
        self._stats_label.setText(f"Завершено помидоров: {self._pomodoro_count}")

    def _tick(self) -> None:
        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self._timer.stop()
            self._is_running = False
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
            if self._is_work_mode:
                self._pomodoro_count += 1
            self.timer_finished.emit()
            self._switch_mode()
            return
        self._update_display()

    def _switch_mode(self) -> None:
        self._is_work_mode = not self._is_work_mode
        self._remaining_seconds = WORK_SECONDS if self._is_work_mode else BREAK_SECONDS
        self._update_display()
        self._apply_mode_style()
        self.mode_changed.emit("work" if self._is_work_mode else "break")

    def _on_start(self) -> None:
        self._is_running = True
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._timer.start(1000)

    def _on_pause(self) -> None:
        self._is_running = False
        self._timer.stop()
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)

    def _on_reset(self) -> None:
        self._timer.stop()
        self._is_running = False
        self._remaining_seconds = WORK_SECONDS if self._is_work_mode else BREAK_SECONDS
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._update_display()

    def _on_switch_break(self) -> None:
        was_running = self._is_running
        if self._is_running:
            self._timer.stop()
            self._is_running = False
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
        self._switch_mode()
        if was_running:
            self._on_start()

    def get_pomodoro_count(self) -> int:
        """Возвращает количество завершённых помидоров (для сохранения состояния)."""
        return self._pomodoro_count

    def get_remaining_seconds(self) -> int:
        """Оставшееся время в секундах."""
        return self._remaining_seconds
