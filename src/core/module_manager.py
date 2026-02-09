"""
Менеджер модулей — загрузка и выгрузка модулей из папки modules/.
Поддержка ленивой загрузки и поиска по module_id.
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
        self._loaded_by_id: dict[str, BaseModule] = {}
        self._module_id_to_name: dict[str, str] = {}

    def get_available_modules(self) -> list[str]:
        """
        Возвращает список имён доступных модулей (имена файлов без .py).
        Сканирует папку modules/, не загружая модули.
        """
        names: list[str] = []
        if not self._modules_path.exists():
            return names
        for p in sorted(self._modules_path.iterdir()):
            if p.suffix == ".py" and p.name != "__init__.py" and not p.name.startswith("_"):
                names.append(p.stem)
        return names

    def get_module_by_id(self, module_id: str) -> Optional[BaseModule]:
        """
        Возвращает модуль по его module_id. Ленивая загрузка: загружает при первом обращении.
        """
        if module_id in self._loaded_by_id:
            return self._loaded_by_id[module_id]
        if module_id in self._module_id_to_name:
            return self.load_module(self._module_id_to_name[module_id])
        for name in self.get_available_modules():
            mod = self.load_module(name)
            if mod is not None and mod.module_id == module_id:
                return mod
        return None

    def load_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Динамически загружает модуль по имени (имя файла без .py).
        Возвращает экземпляр класса, наследующего BaseModule, или None при ошибке.
        Ленивая загрузка: загружает только при первом вызове.
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
                self._loaded_by_id[instance.module_id] = instance
                self._module_id_to_name[instance.module_id] = module_name
                return instance

        return None

    def unload_module(self, module_name: str) -> bool:
        """Выгружает модуль по имени. Возвращает True при успехе."""
        if module_name not in self._loaded_modules:
            return False

        module_instance = self._loaded_modules[module_name]
        mid = module_instance.module_id
        module_instance.on_unload()
        del self._loaded_modules[module_name]
        if mid in self._loaded_by_id:
            del self._loaded_by_id[mid]
        if mid in self._module_id_to_name:
            del self._module_id_to_name[mid]

        spec_name = f"modules.{module_name}"
        if spec_name in sys.modules:
            del sys.modules[spec_name]

        return True

    def get_modules(self) -> dict[str, BaseModule]:
        """Возвращает словарь загруженных модулей: имя -> экземпляр."""
        return self._loaded_modules.copy()
