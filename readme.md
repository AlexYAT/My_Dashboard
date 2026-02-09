# Personal Dashboard

Десктопное приложение на Python + PySide6 для личной продуктивности.

## Структура проекта

```
My_Dashboard/
├── src/
│   ├── core/
│   │   ├── dashboard_app.py   # Главное окно (QMainWindow)
│   │   ├── base_module.py     # Базовый класс модулей
│   │   └── module_manager.py # Загрузка модулей из modules/
│   ├── modules/
│   │   └── welcome_module.py  # Пример модуля
│   └── main.py                # Точка входа
├── requirements.txt
├── .gitignore
└── README.md
```

## Ядро приложения

- **DashboardApp** — главное окно с центральной областью для виджетов модулей и меню (Файл → Выход).
- **BaseModule** — абстрактный класс модуля: `get_name()`, `get_widget()`, `on_load()`, `on_unload()`, свойства `module_id`, `version`, `author`, `description`.
- **ModuleManager** — загрузка/выгрузка модулей из папки `src/modules/`: `load_module()`, `unload_module()`, `get_modules()`.

Новый модуль: класс в `src/modules/`, наследник `BaseModule`; загрузка через `get_module_manager().load_module("имя_файла")` и `register_module(module)`.

## Быстрый старт

1. Создать виртуальное окружение:

   ```bash
   python -m venv venv
   ```

2. Активировать окружение:

   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Запустить приложение:

   ```bash
   python src/main.py
   ```

Откроется окно «Personal Dashboard v0.1» с меню и приветственным модулем.
