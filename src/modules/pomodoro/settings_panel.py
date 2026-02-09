"""
Панель настроек Pomodoro: время работы/перерывов, помидоров до длинного перерыва, звук.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .pomodoro_settings import (
    WORK_OPTIONS,
    SHORT_BREAK_OPTIONS,
    LONG_BREAK_OPTIONS,
    PomodoroSettings,
)


def _format_min(sec: int) -> str:
    return f"{sec // 60} мин"


class SettingsPanel(QWidget):
    """Виджет настроек: интервалы, счётчик сессий, звук."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Интервалы
        intervals = QGroupBox("Интервалы")
        form = QFormLayout(intervals)

        self._work_combo = QComboBox()
        for s in WORK_OPTIONS:
            self._work_combo.addItem(_format_min(s), s)
        self._work_combo.setCurrentIndex(1)
        form.addRow("Время работы:", self._work_combo)

        self._short_combo = QComboBox()
        for s in SHORT_BREAK_OPTIONS:
            self._short_combo.addItem(_format_min(s), s)
        self._short_combo.setCurrentIndex(1)
        form.addRow("Короткий перерыв:", self._short_combo)

        self._long_combo = QComboBox()
        for s in LONG_BREAK_OPTIONS:
            self._long_combo.addItem(_format_min(s), s)
        form.addRow("Длинный перерыв:", self._long_combo)

        self._tomatoes_combo = QComboBox()
        for i in range(1, 11):
            self._tomatoes_combo.addItem(str(i), i)
        self._tomatoes_combo.setCurrentIndex(3)
        form.addRow("Помидоров до длинного перерыва:", self._tomatoes_combo)

        layout.addWidget(intervals)

        # Звук
        sound_group = QGroupBox("Звук")
        sound_layout = QVBoxLayout(sound_group)
        self._sound_check = QCheckBox("Включить звуковые уведомления")
        self._sound_check.setChecked(True)
        sound_layout.addWidget(self._sound_check)
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Громкость:"))
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(70)
        vol_layout.addWidget(self._volume_slider)
        sound_layout.addLayout(vol_layout)
        layout.addWidget(sound_group)

        layout.addStretch()

    def get_settings(self) -> PomodoroSettings:
        s = PomodoroSettings(
            work_seconds=self._work_combo.currentData(),
            short_break_seconds=self._short_combo.currentData(),
            long_break_seconds=self._long_combo.currentData(),
            tomatoes_until_long_break=self._tomatoes_combo.currentData(),
            sound_enabled=self._sound_check.isChecked(),
            sound_volume=self._volume_slider.value() / 100.0,
        )
        s.validate()
        return s

    def set_settings(self, settings: PomodoroSettings) -> None:
        settings.validate()
        for i in range(self._work_combo.count()):
            if self._work_combo.itemData(i) == settings.work_seconds:
                self._work_combo.setCurrentIndex(i)
                break
        for i in range(self._short_combo.count()):
            if self._short_combo.itemData(i) == settings.short_break_seconds:
                self._short_combo.setCurrentIndex(i)
                break
        for i in range(self._long_combo.count()):
            if self._long_combo.itemData(i) == settings.long_break_seconds:
                self._long_combo.setCurrentIndex(i)
                break
        idx = min(settings.tomatoes_until_long_break - 1, 9)
        self._tomatoes_combo.setCurrentIndex(idx)
        self._sound_check.setChecked(settings.sound_enabled)
        self._volume_slider.setValue(int(settings.sound_volume * 100))
