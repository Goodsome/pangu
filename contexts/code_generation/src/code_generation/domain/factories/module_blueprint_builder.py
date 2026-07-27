import builtins
from dataclasses import dataclass, field
from typing import Self

from code_dom.domain.value_objects.ast_stmt import AstStmtBase
from foundation.common_types.fqns.fqn import ModuleFqn

from code_generation.domain.entities.module_blueprint import ModuleBlueprint


@dataclass
class ModuleBlueprintBuilder:
    path: ModuleFqn
    needed_symbols: set[str] = field(default_factory=set)
    body: list[AstStmtBase] = field(default_factory=list)

    def with_symbol(self, name: str) -> Self:
        if not hasattr(builtins, name):
            self.needed_symbols.add(name)
        return self

    def with_symbols(self, names: list[str]) -> Self:
        for name in names:
            self.with_symbol(name)
        return self

    def with_stmt(self, stmt: AstStmtBase) -> Self:
        self.body.append(stmt)
        return self

    def build(self) -> ModuleBlueprint:
        return ModuleBlueprint(
            path=self.path,
            needed_symbols=self.needed_symbols,
            body=self.body,
        )
