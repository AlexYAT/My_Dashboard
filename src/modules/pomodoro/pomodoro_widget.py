"""
Виджет Pomodoro: круговая диаграмма, настраиваемые интервалы, счётчик сессий,
звуки, текущая задача, статистика, горячие клавиши, экспорт.
"""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .circular_progress import CircularProgressWidget
from .pomodoro_settings import (
    load_settings,
    save_settings,
    PomodoroSettings,
)
from .pomodoro_sounds import PomodoroSounds
from .pomodoro_stats import (
    PomodoroRecord,
    add_record,
    get_today_count,
    get_week_count,
    get_month_count,
    export_csv,
    export_json,
)
from .settings_panel import SettingsPanel


class PomodoroWidget(QWidget):
    """Полнофункциональный виджет Pomodoro по методологии."""

    timer_finished = Signal()
    mode_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._settings = load_settings()
        self._sounds = PomodoroSounds()
        self._sounds.set_enabled(self._settings.sound_enabled)
        self._sounds.set_volume(self._settings.sound_volume)

        self._work_seconds = self._settings.work_seconds
        self._short_break_seconds = self._settings.short_break_seconds
        self._long_break_seconds = self._settings.long_break_seconds
        self._tomatoes_until_long = self._settings.tomatoes_until_long_break

        self._total_seconds = self._work_seconds
        self._remaining_seconds = self._work_seconds
        self._elapsed_in_interval = 0.0
        self._is_work_mode = True
        self._is_long_break = False
        self._is_running = False
        self._is_paused = False
        self._pomodoro_count = 0
        self._pomodoro_in_session = 0
        self._current_task = ""
        self._interval_started_at: datetime | None = None

        self._timer_sec = QTimer(self)
        self._timer_sec.timeout.connect(self._tick_sec)
        self._timer_smooth = QTimer(self)
        self._timer_smooth.timeout.connect(self._tick_smooth)

        self._setup_ui()
        self._setup_hotkeys()
        self._update_display()
        self._apply_state_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setMinimumWidth(360)
        self.setObjectName("pomodoroWidget")

        # Режим
        self._mode_label = QLabel("РЕЖИМ РАБОТЫ")
        self._mode_label.setObjectName("modeLabel")
        self._mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_mode = QFont()
        font_mode.setPointSize(12)
        font_mode.setBold(True)
        self._mode_label.setFont(font_mode)
        self._mode_label.setToolTip("Текущий режим: работа или перерыв")
        layout.addWidget(self._mode_label)

        # Круговая диаграмма + время
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._circle = CircularProgressWidget(self)
        self._circle.setToolTip("Прогресс текущего интервала")
        center.addWidget(self._circle, 0, Qt.AlignmentFlag.AlignCenter)

        self._time_label = QLabel("25:00")
        self._time_label.setObjectName("timeLabel")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_time = QFont("Consolas", 42, QFont.Weight.Bold)
        self._time_label.setFont(font_time)
        self._time_label.setToolTip("Оставшееся время (MM:SS)")
        center.addWidget(self._time_label)
        layout.addLayout(center)

        # Текущая задача (заглушка для интеграции с ToDo)
        task_group = QGroupBox("Текущая задача")
        task_layout = QVBoxLayout(task_group)
        self._task_edit = QLineEdit()
        self._task_edit.setPlaceholderText("Введите задачу на этот помидор (или выберите из ToDo позже)")
        self._task_edit.setToolTip("Задача, над которой работаете в этом помидоре")
        task_layout.addWidget(self._task_edit)
        layout.addWidget(task_group)

        # Кнопки
        buttons = QGridLayout()
        self._btn_start = QPushButton("▶ Старт")
        self._btn_start.setObjectName("btnStart")
        self._btn_start.setToolTip("Запустить таймер (Ctrl+Shift+P)")
        self._btn_start.clicked.connect(self._on_start)
        buttons.addWidget(self._btn_start, 0, 0)

        self._btn_pause = QPushButton("⏸ Пауза")
        self._btn_pause.setObjectName("btnPause")
        self._btn_pause.setEnabled(False)
        self._btn_pause.setToolTip("Приостановить таймер (Ctrl+Shift+P)")
        self._btn_pause.clicked.connect(self._on_pause)
        buttons.addWidget(self._btn_pause, 0, 1)

        self._btn_reset = QPushButton("↻ Сброс")
        self._btn_reset.setObjectName("btnReset")
        self._btn_reset.setToolTip("Сбросить таймер на начало интервала (Ctrl+Shift+R)")
        self._btn_reset.clicked.connect(self._on_reset)
        buttons.addWidget(self._btn_reset, 1, 0)

        self._btn_skip = QPushButton("⏭ Пропустить")
        self._btn_skip.setObjectName("btnSkip")
        self._btn_skip.setToolTip("Перейти к следующему интервалу (Ctrl+Shift+S)")
        self._btn_skip.clicked.connect(self._on_skip)
        buttons.addWidget(self._btn_skip, 1, 1)

        layout.addLayout(buttons)

        # Доп. кнопки: перерыв вручную, настройки, экспорт
        extra = QHBoxLayout()
        self._btn_break = QPushButton("🔄 Перерыв")
        self._btn_break.setObjectName("btnBreak")
        self._btn_break.setToolTip("Вручную переключиться на короткий перерыв")
        self._btn_break.clicked.connect(self._on_switch_break)
        extra.addWidget(self._btn_break)

        self._btn_settings = QPushButton("⚙ Настройки")
        self._btn_settings.setObjectName("btnSettings")
        self._btn_settings.setToolTip("Интервалы, звук, помидоров до длинного перерыва")
        self._btn_settings.clicked.connect(self._on_settings)
        extra.addWidget(self._btn_settings)

        self._btn_export = QPushButton("📤 Экспорт")
        self._btn_export.setToolTip("Экспорт статистики в CSV или JSON")
        self._btn_export.clicked.connect(self._on_export)
        extra.addWidget(self._btn_export)

        layout.addLayout(extra)

        # Статистика
        self._stats_label = QLabel("Завершено в сессии: 0")
        self._stats_label.setObjectName("statsLabel")
        self._stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stats_label.setToolTip("Помидоров завершено в текущей сессии (до длинного перерыва)")
        layout.addWidget(self._stats_label)

        self._period_stats_label = QLabel("Сегодня: 0 | Неделя: 0 | Месяц: 0")
        self._period_stats_label.setObjectName("periodStatsLabel")
        self._period_stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._period_stats_label.setToolTip("Статистика за период")
        layout.addWidget(self._period_stats_label)

        self._base_styles = self._get_base_styles()
        self._set_styles()

    def _get_base_styles(self) -> str:
        return """
            #pomodoroWidget { border-radius: 12px; border: 1px solid #404040; }
            #modeLabel { }
            #timeLabel { color: #ffffff; letter-spacing: 2px; }
            #btnStart { background-color: #2e7d32; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            #btnStart:hover { background-color: #388e3c; }
            #btnStart:disabled { background-color: #555; color: #999; }
            #btnPause { background-color: #c62828; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            #btnPause:hover { background-color: #d32f2f; }
            #btnPause:disabled { background-color: #555; color: #999; }
            #btnReset { background-color: #ef6c00; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            #btnReset:hover { background-color: #f57c00; }
            #btnSkip { background-color: #6a1b9a; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            #btnSkip:hover { background-color: #7b1fa2; }
            #btnBreak { background-color: #1565c0; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; }
            #btnBreak:hover { background-color: #1976d2; }
            #btnSettings { background-color: #455a64; color: white; border: none; border-radius: 8px; padding: 10px 16px; }
            #btnSettings:hover { background-color: #546e7a; }
            #statsLabel, #periodStatsLabel { color: #b0b0b0; font-size: 13px; }
        """

    def _set_styles(self) -> None:
        self._apply_state_style()

    def _apply_state_style(self) -> None:
        if self._is_paused:
            self._mode_label.setText("ПАУЗА")
            style = (
                "#pomodoroWidget { background-color: #3d3d00; border-color: #ffc107; }\n"
                "#modeLabel { color: #ffc107; }"
            )
        elif self._is_work_mode:
            self._mode_label.setText("РЕЖИМ РАБОТЫ")
            style = (
                "#pomodoroWidget { background-color: #1b3d1f; border-color: #2e7d32; }\n"
                "#modeLabel { color: #81c784; }"
            )
        else:
            if self._is_long_break:
                self._mode_label.setText("ДЛИННЫЙ ПЕРЕРЫВ")
            else:
                self._mode_label.setText("РЕЖИМ ОТДЫХА")
            style = (
                "#pomodoroWidget { background-color: #0d2137; border-color: #1565c0; }\n"
                "#modeLabel { color: #64b5f6; }"
            )
        self.setStyleSheet(self._base_styles + style)
        self._circle.set_work_mode(self._is_work_mode)
        self._circle.set_paused(self._is_paused)

    def _setup_hotkeys(self) -> None:
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, self._toggle_start_pause)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self._on_reset)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._on_skip)

    def _toggle_start_pause(self) -> None:
        if self._is_running:
            self._on_pause()
        else:
            self._on_start()

    def _update_display(self) -> None:
        m = self._remaining_seconds // 60
        s = self._remaining_seconds % 60
        self._time_label.setText(f"{m:02d}:{s:02d}")
        self._stats_label.setText(f"Завершено в сессии: {self._pomodoro_in_session} (всего: {self._pomodoro_count})")
        self._period_stats_label.setText(
            f"Сегодня: {get_today_count()} | Неделя: {get_week_count()} | Месяц: {get_month_count()}"
        )
        total = self._total_seconds
        elapsed = total - self._remaining_seconds + self._elapsed_in_interval
        self._circle.set_progress(total, elapsed)

    def _tick_sec(self) -> None:
        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self._finish_interval()
            return
        self._update_display()

    def _tick_smooth(self) -> None:
        self._elapsed_in_interval += 0.1
        self._update_display()

    def _finish_interval(self) -> None:
        self._timer_sec.stop()
        self._timer_smooth.stop()
        self._is_running = False
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)

        finished_at = datetime.now().isoformat()
        started_at = self._interval_started_at.isoformat() if self._interval_started_at else finished_at
        duration = self._total_seconds
        task_name = self._task_edit.text().strip() or ""

        if self._is_work_mode:
            self._pomodoro_count += 1
            self._pomodoro_in_session += 1
            add_record(PomodoroRecord(
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                mode="work",
                task_name=task_name,
            ))
            self._sounds.play_end_work()
            self.timer_finished.emit()
            self._switch_to_break()
        else:
            add_record(PomodoroRecord(
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                mode="long_break" if self._is_long_break else "short_break",
                task_name="",
            ))
            self._sounds.play_end_break()
            if self._is_long_break:
                self._pomodoro_in_session = 0
            self._switch_to_work()
            self._update_display()
            self._apply_state_style()
            return

        self._update_display()
        self._apply_state_style()

    def _switch_to_break(self) -> None:
        if self._pomodoro_in_session >= self._tomatoes_until_long:
            self._is_long_break = True
            self._total_seconds = self._long_break_seconds
            self._sounds.play_start_break()
        else:
            self._is_long_break = False
            self._total_seconds = self._short_break_seconds
            self._sounds.play_start_break()
        self._is_work_mode = False
        self._remaining_seconds = self._total_seconds
        self._elapsed_in_interval = 0.0
        self._interval_started_at = datetime.now()
        self._update_display()
        self._apply_state_style()
        self.mode_changed.emit("break")
        self._timer_sec.start(1000)
        self._timer_smooth.start(100)
        self._is_running = True
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)

    def _switch_to_work(self) -> None:
        self._is_work_mode = True
        self._is_long_break = False
        self._total_seconds = self._work_seconds
        self._remaining_seconds = self._work_seconds
        self._elapsed_in_interval = 0.0
        self._interval_started_at = None
        self._update_display()
        self._apply_state_style()
        self.mode_changed.emit("work")

    def _on_start(self) -> None:
        self._is_paused = False
        self._interval_started_at = datetime.now()
        self._elapsed_in_interval = 0.0
        if self._is_work_mode:
            self._sounds.play_start_work()
        else:
            self._sounds.play_start_break()
        self._is_running = True
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._timer_sec.start(1000)
        self._timer_smooth.start(100)

    def _on_pause(self) -> None:
        self._is_running = False
        self._is_paused = True
        self._timer_sec.stop()
        self._timer_smooth.stop()
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._apply_state_style()

    def _on_reset(self) -> None:
        self._timer_sec.stop()
        self._timer_smooth.stop()
        self._is_running = False
        self._is_paused = False
        self._remaining_seconds = self._total_seconds
        self._elapsed_in_interval = 0.0
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._update_display()
        self._apply_state_style()

    def _on_skip(self) -> None:
        was_running = self._is_running
        if self._is_running:
            self._timer_sec.stop()
            self._timer_smooth.stop()
            self._is_running = False
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
        if self._is_work_mode:
            self._switch_to_break()
        else:
            if self._is_long_break:
                self._pomodoro_in_session = 0
            self._switch_to_work()
        if was_running:
            self._btn_start.setEnabled(False)
            self._btn_pause.setEnabled(True)
            self._timer_sec.start(1000)
            self._timer_smooth.start(100)
            self._is_running = True

    def _on_switch_break(self) -> None:
        was_running = self._is_running
        if self._is_running:
            self._timer_sec.stop()
            self._timer_smooth.stop()
            self._is_running = False
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
        self._switch_to_break()
        if was_running:
            self._timer_sec.start(1000)
            self._timer_smooth.start(100)
            self._is_running = True
            self._btn_start.setEnabled(False)
            self._btn_pause.setEnabled(True)

    def _on_settings(self) -> None:
        dialog = QWidget()
        dialog.setWindowTitle("Настройки Pomodoro")
        layout = QVBoxLayout(dialog)
        panel = SettingsPanel()
        panel.set_settings(self._settings)
        layout.addWidget(panel)
        ok_btn = QPushButton("Применить")
        def apply_and_close():
            self._settings = panel.get_settings()
            save_settings(self._settings)
            self._work_seconds = self._settings.work_seconds
            self._short_break_seconds = self._settings.short_break_seconds
            self._long_break_seconds = self._settings.long_break_seconds
            self._tomatoes_until_long = self._settings.tomatoes_until_long_break
            self._sounds.set_enabled(self._settings.sound_enabled)
            self._sounds.set_volume(self._settings.sound_volume)
            if not self._is_running:
                self._total_seconds = self._work_seconds if self._is_work_mode else (
                    self._long_break_seconds if self._is_long_break else self._short_break_seconds
                )
                self._remaining_seconds = self._total_seconds
                self._update_display()
            dialog.close()
        ok_btn.clicked.connect(apply_and_close)
        layout.addWidget(ok_btn)
        dialog.resize(400, 380)
        dialog.show()

    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт статистики",
            "",
            "CSV (*.csv);;JSON (*.json);;Все файлы (*)",
        )
        if not path:
            return
        p = Path(path)
        if p.suffix.lower() == ".json":
            ok = export_json(p)
        else:
            ok = export_csv(p)
        if ok:
            QMessageBox.information(self, "Экспорт", f"Сохранено: {path}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл.")

    def get_pomodoro_count(self) -> int:
        return self._pomodoro_count

    def get_remaining_seconds(self) -> int:
        return self._remaining_seconds
