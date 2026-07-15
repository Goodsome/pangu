from dataclasses import dataclass
from typing import override

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
        import_symbols: set[str] = set()
        for module_blueprint in modules:
            import_symbols.update(module_blueprint.collect_import_symbols())

        symbols = self.code_structure_api.get_symbols(list(import_symbols))

        name_module_map: dict[str, str] = {s.name: s.module_fqn for s in symbols}
        code_documents = [
            module_blueprint_to_code_document(module_blueprint, name_module_map)
            for module_blueprint in modules
        ]
        self.code_dom_api.save_documents(code_documents)
