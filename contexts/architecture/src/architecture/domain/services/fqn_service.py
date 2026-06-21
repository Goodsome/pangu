from dataclasses import dataclass
from pathlib import Path

from architecture.domain.value_objects.fqn import ModuleFqn


@dataclass
class FqnService:

    _CONTEXT_REGISTRY: dict[str, str] = {
        "architecture": "contexts/architecture/src"
    }

    def build_module_fqn(self, path: Path) -> ModuleFqn:
        ...

    @classmethod
    def build_path(cls, fqn: ModuleFqn, is_package: bool = False) -> Path:
        if fqn.context not in cls._CONTEXT_REGISTRY:
            raise ValueError(f"Unknown context: {fqn.context}")
        context_path = Path(cls._CONTEXT_REGISTRY[fqn.context])
        path = context_path / "/".join(fqn.parts)
        if is_package:
            path /= "__init__.py"
        else:
            path = path.with_suffix(".py")
        return path
