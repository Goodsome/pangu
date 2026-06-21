from dataclasses import dataclass
from pathlib import Path

from architecture.domain.services.context_registry import ContextRegistry
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.enums.context_name import ContextName

@dataclass
class FqnService:

    def build_module_fqn(self, path: Path) -> ModuleFqn:
        ...

    @staticmethod
    def build_path(fqn: ModuleFqn) -> Path:
        context_name = ContextName(fqn.context)
        root_path = ContextRegistry.get_context_root_path(context_name)
        path = root_path / "/".join(fqn.parts)
        return path
        