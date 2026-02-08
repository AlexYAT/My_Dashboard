"""
Менеджер модулей — загрузка и выгрузка модулей из папки modules/.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional

from .base_module import BaseModule


class ModuleManager:
    """Управляет загрузкой и выгрузкой модулей дашборда."""

    def __init__(self, modules_path: Optional[Path] = None):
        if modules_path is None:
            modules_path = Path(__file__).resolve().parent.parent / "modules"
        self._modules_path = Path(modules_path)
        self._loaded_modules: dict[str, BaseModule] = {}

    def load_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Динамически загружает модуль по имени (имя файла без .py).
        Возвращает экземпляр класса, наследующего BaseModule, или None при ошибке.
        """
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]

        module_file = self._modules_path / f"{module_name}.py"
        if not module_file.exists():
            return None

        spec = importlib.util.spec_from_file_location(
            f"modules.{module_name}",
            module_file,
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        # Ищем класс-наследник BaseModule в модуле
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseModule)
                and attr is not BaseModule
            ):
                instance = attr()
                instance.on_load()
                self._loaded_modules[module_name] = instance
                return instance

        return None

    def unload_module(self, module_name: str) -> bool:
        """Выгружает модуль по имени. Возвращает True при успехе."""
        if module_name not in self._loaded_modules:
            return False

        module_instance = self._loaded_modules[module_name]
        module_instance.on_unload()
        del self._loaded_modules[module_name]

        # Удаляем модуль из sys.modules, чтобы при повторной загрузке он подтянулся заново
        spec_name = f"modules.{module_name}"
        if spec_name in sys.modules:
            del sys.modules[spec_name]

        return True

    def get_modules(self) -> dict[str, BaseModule]:
        """Возвращает словарь загруженных модулей: имя -> экземпляр."""
        return self._loaded_modules.copy()
