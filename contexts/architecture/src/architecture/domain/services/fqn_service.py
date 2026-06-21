from dataclasses import dataclass
from pathlib import Path

from architecture.domain.value_objects.fqn import ModuleFqn

_CONTEXT_REGISTRY: dict[str, str] = {
    "architecture": "contexts/architecture/src"
}

@dataclass
class FqnService:

    def build_module_fqn(self, path: Path) -> ModuleFqn:
        ...

    @staticmethod
    def build_path(fqn: ModuleFqn, is_package: bool = False) -> Path:
        if fqn.context not in _CONTEXT_REGISTRY:
            raise ValueError(f"Unknown context: {fqn.context}")
        context_path = Path(_CONTEXT_REGISTRY[fqn.context])
        path = context_path / "/".join(fqn.parts)
        if is_package:
            path /= "__init__.py"
        else:
            path = path.with_suffix(".py")
        return path
