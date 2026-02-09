"""
Загрузчик модуля Pomodoro для ModuleManager.
load_module("pomodoro") загружает этот файл и находит класс PomodoroModule.
"""

try:
    from src.modules.pomodoro.pomodoro_module import PomodoroModule
except ImportError:
    from .pomodoro.pomodoro_module import PomodoroModule
