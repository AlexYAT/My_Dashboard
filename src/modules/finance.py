"""
Загрузчик модуля Финансов для ModuleManager.
load_module("finance") загружает этот файл и находит класс FinanceModule.
"""

try:
    from src.modules.finance.finance_module import FinanceModule
except ImportError:
    from .finance.finance_module import FinanceModule
