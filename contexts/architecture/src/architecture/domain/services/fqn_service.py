from dataclasses import dataclass
from pathlib import Path
from architecture.domain.services.context_registry import ContextRegistry
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.domain.enums.context_name import ContextName
from architecture.domain.value_objects.parsed_module import ParsedModule


@dataclass
class FqnService:
    @classmethod
    def build_module_fqn(cls, path: Path) -> ModuleFqn:
        rel_path = ContextRegistry.get_relative_path(path)
        if rel_path.name == "__init__.py":
            return ModuleFqn(".".join(rel_path.parent.parts))
        return ModuleFqn(".".join(rel_path.with_suffix("").parts))

    @staticmethod
    def build_path(fqn: ModuleFqn, is_package: bool) -> Path:
        context_name = ContextName(fqn.context)
        root_path = ContextRegistry.get_context_root_path(context_name)
        path = root_path / "/".join(fqn.parts)
        if not is_package:
            path = path.with_suffix(".py")
        return path

    @classmethod
    def collect_fqns(cls, parsed_modules: list[ParsedModule]) -> set[ModuleFqn]:
        fqns: set[ModuleFqn] = set()
        for parsed_module in parsed_modules:
            module_fqn = parsed_module.fqn
            fqns.add(module_fqn)
            if not module_fqn.is_root:
                fqns.add(module_fqn.parent_fqn)
            for import_str in parsed_module.import_module_fqns:
                fqns.add(import_str)
        return fqns
