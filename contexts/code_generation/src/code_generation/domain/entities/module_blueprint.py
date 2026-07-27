import builtins
from collections.abc import Mapping
from pathlib import Path

from architecture.domain.services.fqn_service import FqnService
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.value_objects.ast_stmt import AstAlias, AstImportFrom, AstStmtBase
from foundation.building_blocks.entity import Entity
from foundation.common_types.fqns.fqn import ModuleFqn
from pydantic import Field


class ModuleBlueprint(Entity):
    path: ModuleFqn
    needed_symbols: set[str] = Field(default_factory=set)
    body: list[AstStmtBase] = Field(default_factory=list)

    def collect_local_symbols(self) -> set[str]:
        local_symbols: set[str] = set()
        for stmt in self.body:
            if hasattr(stmt, "name") and isinstance(getattr(stmt, "name"), str):
                local_symbols.add(getattr(stmt, "name"))
        return local_symbols

    def to_physical_path(self) -> Path:
        return FqnService.build_path(self.path, is_package=False)

    def to_code_document(self, name_module_map: Mapping[str, str]) -> CodeDocument:
        path_obj = self.to_physical_path()
        local_symbols = self.collect_local_symbols()
        external_symbols = self.needed_symbols - local_symbols

        imports_body: list[AstImportFrom] = []

        for name in sorted(external_symbols):
            if name in name_module_map and not hasattr(builtins, name):
                imports_body.append(
                    AstImportFrom(
                        module=name_module_map[name],
                        names=[AstAlias(name=name, asname=None)],
                    )
                )

        return CodeDocument(
            id=path_obj,
            physical_path=path_obj,
            body=imports_body + self.body,
            description=None,
        )
