from dataclasses import dataclass
from pathlib import Path

from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.domain.value_objects.parsed_module import ParsedModule


@dataclass
class GraphBuilder:
    root_path: Path
    
    def build_from_parsed_modules(self, parsed_modules: list[ParsedModule]) -> list[Module]:
        module_map: dict[ModuleFqn, Module] = {}
        for parsed_module in parsed_modules:
            fqn = self._path_to_fqn(parsed_module.file_path)
            is_package = parsed_module.file_path.name == "__init__.py"
            module = Module(
                id=ModuleId.create(),
                fqn=fqn,
                name=fqn.symbol,
                is_package=is_package,
            )
            module_map[module.fqn] = module

        for parsed_module in parsed_modules:
            fqn = self._path_to_fqn(parsed_module.file_path)
            source_module = module_map[fqn]

            for import_str in parsed_module.raw_imports:
                if not import_str.startswith("architecture"):
                    continue
                target_fqn = self._module_path_to_fqn(import_str)
                if target_fqn not in module_map:
                    continue
                target_module = module_map[target_fqn]
                source_module.add_dependency(target_module_id=target_module.id)

        return list(module_map.values())

    def _path_to_fqn(self, path: Path) -> ModuleFqn:
        rel_path = path.relative_to(self.root_path)
        if rel_path.name == "__init__.py":
            return ModuleFqn(".".join(rel_path.parent.parts))
        return ModuleFqn(".".join(rel_path.with_suffix("").parts))

    def _module_path_to_fqn(self, path: str) -> ModuleFqn:
        return ModuleFqn(path)
