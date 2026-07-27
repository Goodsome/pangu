import builtins
from dataclasses import dataclass
from typing import override

from architecture.domain.services.fqn_service import FqnService
from code_dom.interfaces.api import CodeDomApi
from code_structure.interfaces.api import CodeStructureApi

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.ports.generator import Generator
from code_generation.infrastructure.mappers.module_blueprint_to_code_document import (
    module_blueprint_to_code_document,
)


@dataclass
class CodeDomGenerator(Generator):
    code_dom_api: CodeDomApi
    code_structure_api: CodeStructureApi

    @override
    def write_modules(self, modules: list[ModuleBlueprint]) -> None:
        name_module_map = self._query_name_module_map(modules)
        code_documents = [
            module_blueprint_to_code_document(module_blueprint, name_module_map)
            for module_blueprint in modules
        ]
        self.code_dom_api.save_documents(code_documents)

    @override
    def remove_modules(self, modules: list[ModuleBlueprint]) -> None:
        paths = [FqnService.build_path(module.path, is_package=False) for module in modules]
        self.code_dom_api.delete_documents(paths)

    def _query_name_module_map(self, modules: list[ModuleBlueprint]) -> dict[str, str]:
        import_symbols: set[str] = set()
        name_module_map: dict[str, str] = {}
        for module in modules:
            import_symbols.update(
                {s for s in module.collect_import_symbols() if not hasattr(builtins, s)}
            )

            for symbol_def in module.symbols:
                name_module_map[symbol_def.name] = module.path

        if import_symbols:
            symbols = self.code_structure_api.get_symbols(list(import_symbols))
            for symbol in symbols:
                name_module_map[symbol.name] = symbol.module_fqn
        return name_module_map
