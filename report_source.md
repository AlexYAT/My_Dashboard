# Отчёт по исходному коду: Personal Dashboard

**Назначение:** синхронизация Notion ↔ DeepSeek ↔ src (актуальная структура и содержание исходников).

**Дата:** 2025-02-08  
**Проект:** My_Dashboard — десктопное приложение на Python + PySide6 для личной продуктивности.

---

## 1. Обзор проекта

- **Точка входа:** `src/main.py` → создаёт `QApplication` и `DashboardApp`, показывает окно. Модули не загружаются при старте — только по клику в панели навигации.
- **Архитектура:** главное окно (`DashboardApp`, QMainWindow) с панелью модулей слева и центральной областью (QStackedWidget). Модули — наследники `BaseModule`, подгружаются через `ModuleManager` из `src/modules/` (ленивая загрузка).
- **Модули:** Welcome (приветствие), Pomodoro (таймер по методологии Pomodoro с настройками, звуками, статистикой).

---

## 2. Дерево исходных файлов

```
My_Dashboard/
├── .gitignore
├── README.md
├── requirements.txt
├── report_source.md
└── src/
    ├── __init__.py
    ├── main.py
    ├── core/
    │   ├── __init__.py
    │   ├── base_module.py
    │   ├── dashboard_app.py
    │   └── module_manager.py
    └── modules/
        ├── __init__.py
        ├── welcome_module.py
        ├── pomodoro.py
        └── pomodoro/
            ├── __init__.py
            ├── circular_progress.py
            ├── pomodoro_module.py
            ├── pomodoro_settings.py
            ├── pomodoro_sounds.py
            ├── pomodoro_stats.py
            ├── pomodoro_widget.py
            └── settings_panel.py
```

---

## 3. Зависимости и окружение

- **requirements.txt:** PySide6>=6.5.0, cryptography>=41.0.0, pytest>=7.4.0
- **.gitignore:** __pycache__, *.pyc, venv/.venv/env/, .env, .vscode/.idea, *.swp

---

## 4. Содержимое исходных файлов

### 4.1. src/main.py

- **Назначение:** точка входа приложения.
- **Импорты:** sys, pathlib.Path, PySide6.QtWidgets.QApplication, src.core.DashboardApp.
- **Логика:** добавляет корень проекта в sys.path; создаёт QApplication, экземпляр DashboardApp(title="Personal Dashboard", version="0.1"), вызывает show(), exec(). Модули подключаются по нажатию кнопок в панели; последний открытый модуль восстанавливается из конфига.

---

### 4.2. src/__init__.py

- Содержимое: комментарий `# Personal Dashboard - source package`. Пакет верхнего уровня.

---

### 4.3. src/core/__init__.py

- **Экспорт:** BaseModule, DashboardApp, ModuleManager (из .base_module, .dashboard_app, .module_manager).

---

### 4.4. src/core/base_module.py

- **Назначение:** абстрактный базовый класс для всех модулей дашборда.
- **Импорты:** abc (ABC, abstractmethod), PySide6.QtWidgets.QWidget.
- **Класс:** `BaseModule(ABC)`.
  - **Свойства (внутренние + property):** module_id, version, author, description, requires_confirmation (подтверждение перед выходом).
  - **Методы:** get_icon() → str (по умолчанию ""), get_short_name() → str (по умолчанию get_name()), абстрактные get_name(), get_widget() → QWidget, on_load(), on_unload().
- Все модули должны наследовать BaseModule и реализовать абстрактные методы.

---

### 4.5. src/core/module_manager.py

- **Назначение:** загрузка и выгрузка модулей из папки modules/; ленивая загрузка; поиск по module_id.
- **Импорты:** importlib.util, sys, pathlib.Path, typing.Optional, .base_module.BaseModule.
- **Класс:** `ModuleManager`.
  - **__init__(self, modules_path=None):** по умолчанию путь = src/modules; словари _loaded_modules (имя → экземпляр), _loaded_by_id (module_id → экземпляр), _module_id_to_name.
  - **get_available_modules()** → list[str]: сканирует папку modules/, возвращает имена файлов без .py (кроме __init__.py и _*).
  - **get_module_by_id(module_id)** → BaseModule | None: возвращает загруженный или подгружает по имени при первом обращении.
  - **load_module(module_name)** → BaseModule | None: динамическая загрузка через importlib (spec_from_file_location, exec_module), поиск класса-наследника BaseModule в модуле, вызов on_load(), сохранение по имени и по module_id.
  - **unload_module(module_name)** → bool: on_unload(), удаление из словарей и sys.modules.
  - **get_modules()** → dict[str, BaseModule]: копия _loaded_modules.

---

### 4.6. src/core/dashboard_app.py

- **Назначение:** главное окно приложения: панель навигации слева, центральная область — активный модуль (QStackedWidget); сохранение последнего модуля в JSON.
- **Импорты:** json, pathlib.Path, typing.Optional, PySide6.QtGui (QAction, QKeySequence), PySide6.QtWidgets (QApplication, QFrame, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QStackedWidget, QHBoxLayout, QVBoxLayout, QWidget), .base_module.BaseModule, .module_manager.ModuleManager.
- **Вспомогательная функция:** _config_path() → Path: QStandardPaths.AppConfigLocation / "Personal_Dashboard" / "dashboard_state.json".
- **Класс:** `DashboardApp(QMainWindow)`.
  - **__init__(title, version, modules_path):** создаёт ModuleManager, QStackedWidget, списки кнопок навигации и маппинг имя→индекс; setup_ui(), _restore_last_module().
  - **setup_ui():** центральный QWidget, QHBoxLayout: слева _create_nav_panel() (фиксированная ширина 180px), справа QStackedWidget; меню «Файл» → «Выход»; _apply_global_styles().
  - **_create_nav_panel():** для каждого имени из get_available_modules() — QPushButton (до загрузки отображаемое имя из _display_name_for_module_file), по клику _on_nav_click(module_name).
  - **_display_name_for_module_file(module_name):** welcome_module → "👋 Привет", pomodoro → "🍅 Pomodoro", иначе title из имени.
  - **_on_nav_click(module_name):** если модуль уже в стеке — переключение по индексу; иначе load_module(), addWidget(get_widget()), обновление текста кнопки (get_icon(), get_short_name()); обновление заголовка окна, _save_last_module(), _update_nav_active().
  - **_update_nav_active(active_name):** установка property "active" и setChecked для кнопок.
  - **_apply_global_styles():** QSS для #navPanel, #navButton, #stackedWidget (тёмная тема).
  - **_save_last_module(module_name):** запись {"last_module": module_name} в dashboard_state.json.
  - **_restore_last_module():** чтение JSON, при наличии last_module в списке кнопок — _on_nav_click(last); иначе _open_first_available().
  - **_open_first_available():** предпочтительно welcome_module, иначе первый из get_available_modules().
  - **_on_quit():** если текущий модуль имеет requires_confirmation — QMessageBox «Выйти?»; иначе QApplication.quit().
  - **register_module(module):** заглушка (не используется).
  - **get_module_manager()** → ModuleManager.

---

### 4.7. src/modules/__init__.py

- Содержимое: комментарий `# Modules package`.

---

### 4.8. src/modules/welcome_module.py

- **Назначение:** пример модуля — приветственный блок.
- **Импорты:** PySide6.QtCore.Qt, PySide6.QtWidgets (QLabel, QWidget), src.core.base_module.BaseModule (с fallback core.base_module).
- **Класс:** `WelcomeModule(BaseModule)`.
  - Атрибуты: _module_id="welcome", _version, _author, _description; _widget (QLabel или None).
  - get_name() → "Приветствие", get_icon() → "👋", get_short_name() → "Привет".
  - get_widget(): создаёт QLabel "Добро пожаловать в Personal Dashboard!", выравнивание по центру, стиль шрифта.
  - on_load()/on_unload(): пусто / _widget = None.

---

### 4.9. src/modules/pomodoro.py

- **Назначение:** загрузчик модуля Pomodoro для ModuleManager; load_module("pomodoro") загружает этот файл и находит класс PomodoroModule.
- **Импорты:** src.modules.pomodoro.pomodoro_module.PomodoroModule (с fallback .pomodoro.pomodoro_module). Класс PomodoroModule экспортируется в пространство имён модуля для обнаружения ModuleManager.

---

### 4.10. src/modules/pomodoro/__init__.py

- **Экспорт:** PomodoroModule, PomodoroWidget (из .pomodoro_module, .pomodoro_widget). __all__ = ["PomodoroModule", "PomodoroWidget"].

---

### 4.11. src/modules/pomodoro/pomodoro_module.py

- **Назначение:** объявление модуля Pomodoro для дашборда (наследник BaseModule).
- **Импорты:** BaseModule (src.core или core), PySide6.QtWidgets.QWidget, .pomodoro_widget.PomodoroWidget.
- **Класс:** `PomodoroModule(BaseModule)`.
  - _module_id="pomodoro", _version, _author, _description, _requires_confirmation=True; _widget (PomodoroWidget или None).
  - get_name() → "🍅 Pomodoro Timer", get_icon() → "🍅", get_short_name() → "Pomodoro".
  - get_widget(): при первом обращении создаёт PomodoroWidget().
  - on_load()/on_unload(): пусто / _widget = None.

---

### 4.12. src/modules/pomodoro/circular_progress.py

- **Назначение:** круговая диаграмма прогресса таймера (полный круг = интервал, заполненная часть = прошедшее время).
- **Импорты:** PySide6.QtCore (Qt, QRectF), PySide6.QtGui (QColor, QPainter, QPen, QBrush, QConicalGradient), PySide6.QtWidgets.QWidget.
- **Класс:** `CircularProgressWidget(QWidget)`.
  - Состояние: _total_seconds, _elapsed_seconds, _is_work_mode, _is_paused.
  - set_progress(total_seconds, elapsed_seconds), set_work_mode(work), set_paused(paused).
  - paintEvent: фоновый круг (серый); дуга прогресса — градиент: работа (зелёный→оранжевый→красный), перерыв (синий→голубой), пауза (жёлтый). Старт дуги с 12 часов (90°), обводка 14px.

---

### 4.13. src/modules/pomodoro/pomodoro_settings.py

- **Назначение:** настройки интервалов и звука; загрузка/сохранение в JSON.
- **Константы:** WORK_OPTIONS (20,25,30 мин), SHORT_BREAK_OPTIONS (3,5,10 мин), LONG_BREAK_OPTIONS (15,20,25,30 мин), DEFAULT_TOMATOES_UNTIL_LONG = 4.
- **Класс:** `PomodoroSettings` (dataclass): work_seconds, short_break_seconds, long_break_seconds, tomatoes_until_long_break, sound_enabled, sound_volume. Методы: validate(), to_dict(), from_dict(cls, data).
- **Путь конфига:** _config_path() → AppConfigLocation / "Personal_Dashboard" / "Pomodoro" / "settings.json".
- **Функции:** load_settings() → PomodoroSettings, save_settings(settings).

---

### 4.14. src/modules/pomodoro/pomodoro_sounds.py

- **Назначение:** звуковые уведомления через QSoundEffect; WAV генерируются тонами при первом запуске.
- **Импорты:** math, struct, pathlib.Path, PySide6.QtCore.QUrl, PySide6.QtMultimedia.QSoundEffect.
- **Функции:** _sounds_dir() → AppConfigLocation / "Personal_Dashboard" / "Pomodoro" / "sounds"; _generate_wav(path, frequency, duration_ms, volume) — запись WAV (RIFF, 44.1 kHz, 16 bit, моно); _ensure_sounds() → dict[key→Path] для start_work, end_work, start_break, end_break (создаёт WAV при отсутствии).
- **Класс:** `PomodoroSounds`: set_enabled(), set_volume(); _play(key); play_start_work(), play_end_work(), play_start_break(), play_end_break().

---

### 4.15. src/modules/pomodoro/pomodoro_stats.py

- **Назначение:** история завершённых интервалов; статистика за день/неделю/месяц; экспорт CSV/JSON.
- **Импорты:** csv, json, dataclasses (asdict, dataclass), datetime, pathlib.Path.
- **Класс:** `PomodoroRecord` (dataclass): started_at, finished_at, duration_seconds, mode ("work"|"short_break"|"long_break"), task_name.
- **Путь данных:** _data_path() → AppConfigLocation / "Personal_Dashboard" / "Pomodoro" / "history.json".
- **Функции:** _load_history() → list[dict], _save_history(records); add_record(record); get_records_from(dt) → list[PomodoroRecord]; get_today_count(), get_week_count(), get_month_count() (число записей mode=="work"); get_all_records(); export_csv(file_path) → bool, export_json(file_path) → bool.

---

### 4.16. src/modules/pomodoro/settings_panel.py

- **Назначение:** виджет панели настроек Pomodoro (интервалы, звук).
- **Импорты:** PySide6.QtCore.Qt, PySide6.QtWidgets (QCheckBox, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget), .pomodoro_settings (WORK_OPTIONS, SHORT_BREAK_OPTIONS, LONG_BREAK_OPTIONS, PomodoroSettings).
- **Класс:** `SettingsPanel(QWidget)`: QGroupBox «Интервалы» (work, short break, long break — QComboBox по минутам; помидоров до длинного перерыва 1–10); QGroupBox «Звук» (чекбокс включения, слайдер громкости 0–100). get_settings() → PomodoroSettings, set_settings(settings).

---

### 4.17. src/modules/pomodoro/pomodoro_widget.py

- **Назначение:** основной виджет Pomodoro: круговая диаграмма, настраиваемые интервалы, счётчик сессий (N помидоров → длинный перерыв, сброс после длинного), звуки, текущая задача, статистика, горячие клавиши, экспорт.
- **Импорты:** datetime, pathlib.Path; PySide6.QtCore (QTimer, Qt, Signal), PySide6.QtGui (QFont, QKeySequence, QShortcut), PySide6.QtWidgets (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget); circular_progress.CircularProgressWidget; pomodoro_settings (load_settings, save_settings, PomodoroSettings); pomodoro_sounds.PomodoroSounds; pomodoro_stats (PomodoroRecord, add_record, get_today_count, get_week_count, get_month_count, export_csv, export_json); settings_panel.SettingsPanel.
- **Класс:** `PomodoroWidget(QWidget)`.
  - **Сигналы:** timer_finished, mode_changed(str).
  - **Состояние:** настройки из load_settings(); _work_seconds, _short_break_seconds, _long_break_seconds, _tomatoes_until_long; _total_seconds, _remaining_seconds, _elapsed_in_interval; _is_work_mode, _is_long_break, _is_running, _is_paused; _pomodoro_count, _pomodoro_in_session; _current_task, _interval_started_at. Таймеры: _timer_sec (1 с), _timer_smooth (100 мс) для плавной круговой диаграммы.
  - **UI:** метка режима (РЕЖИМ РАБОТЫ / РЕЖИМ ОТДЫХА / ДЛИННЫЙ ПЕРЕРЫВ / ПАУЗА); CircularProgressWidget; время MM:SS; группа «Текущая задача» (QLineEdit); кнопки Старт, Пауза, Сброс, Пропустить, Перерыв, Настройки, Экспорт; метки «Завершено в сессии» и «Сегодня | Неделя | Месяц».
  - **Стили (QSS):** по состоянию — работа (зелёный фон), перерыв (синий), пауза (жёлтый); кнопки с objectName для цветов.
  - **Горячие клавиши:** Ctrl+Shift+P — старт/пауза, Ctrl+Shift+R — сброс, Ctrl+Shift+S — пропуск интервала.
  - **Логика:** _tick_sec уменьшает _remaining_seconds; при 0 — _finish_interval(): запись PomodoroRecord (work/short_break/long_break), звуки; если работа — _pomodoro_in_session += 1, _switch_to_break() (при _pomodoro_in_session >= _tomatoes_until_long — длинный перерыв, иначе короткий); если перерыв — при длинном сбрасывается _pomodoro_in_session, _switch_to_work(). _switch_to_break() автоматически запускает таймер перерыва; _switch_to_work() только переключает вид, таймер стартует по кнопке. Настройки открываются в отдельном QWidget с SettingsPanel и кнопкой «Применить». Экспорт — QFileDialog, export_csv/export_json по расширению.
  - **Публичные методы:** get_pomodoro_count(), get_remaining_seconds().

---

## 5. Пути к данным и конфигурации

| Назначение | Путь (относительно AppConfigLocation) |
|------------|----------------------------------------|
| Состояние дашборда (последний модуль) | Personal_Dashboard/dashboard_state.json |
| Настройки Pomodoro | Personal_Dashboard/Pomodoro/settings.json |
| История помидоров | Personal_Dashboard/Pomodoro/history.json |
| Звуки Pomodoro (WAV) | Personal_Dashboard/Pomodoro/sounds/*.wav |

AppConfigLocation на Windows: например, `%APPDATA%` (или Roaming); точное значение даёт QStandardPaths.

---

## 6. Поток запуска и навигации

1. Запуск: `python src/main.py` (из корня проекта; корень в sys.path).
2. main(): QApplication, DashboardApp("Personal Dashboard", "0.1"), show().
3. DashboardApp.__init__: ModuleManager(modules_path), setup_ui() (панель кнопок из get_available_modules(), QStackedWidget), _restore_last_module() (из dashboard_state.json или первый доступный).
4. Клик по кнопке модуля: load_module(module_name) при необходимости → get_widget() добавляется в QStackedWidget → переключение на него, заголовок окна, сохранение last_module в JSON.
5. В модуле Pomodoro: виджет загружает настройки и историю из JSON, при завершении интервалов пишет записи в history.json и воспроизводит звуки.

---

## 7. Связи между компонентами (для синхронизации)

- **main.py** зависит от **src.core.DashboardApp**.
- **DashboardApp** зависит от **BaseModule**, **ModuleManager**; читает/пишет **dashboard_state.json**.
- **ModuleManager** зависит от **BaseModule**; загружает файлы из **src/modules/*.py** (и через них пакет **pomodoro/**).
- **WelcomeModule**, **PomodoroModule** наследуют **BaseModule**; **PomodoroModule** создаёт **PomodoroWidget**.
- **PomodoroWidget** использует **CircularProgressWidget**, **PomodoroSettings** (load/save), **PomodoroSounds**, **pomodoro_stats** (add_record, get_*_count, export_*), **SettingsPanel**; при завершении интервалов записывает **PomodoroRecord** в **history.json**.

Конец отчёта.
