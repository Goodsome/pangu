from dataclasses import dataclass
from pathlib import Path
from foundation.system.context_registry import ContextRegistry
from foundation.common_types.fqns.fqn import ModuleFqn
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
        root_path = ContextRegistry.get_context_root_path(fqn.context)
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

    @classmethod
    def collect_fqns_by_type(
        cls, parsed_modules: list[ParsedModule]
    ) -> tuple[set[ModuleFqn], set[ModuleFqn]]:
        file_fqns: set[ModuleFqn] = set()
        package_fqns: set[ModuleFqn] = set()
        for parsed_module in parsed_modules:
            module_fqn = parsed_module.fqn
            if parsed_module.is_package:
                package_fqns.add(module_fqn)
            else:
                file_fqns.add(module_fqn)
            if not module_fqn.is_root:
                package_fqns.add(module_fqn.parent_fqn)
            for import_str in parsed_module.import_module_fqns:
                file_fqns.add(import_str)
                package_fqns.add(import_str)
        return file_fqns, package_fqns
