from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from foundation.common_types.fqns.fqn import ModuleFqn

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.value_objects.import_def import ImportDef
from code_generation.domain.value_objects.symbol_def import ClassDef, SymbolDef


@dataclass
class ModuleBlueprintBuilder:
    path: ModuleFqn
    imports: list[ImportDef] = field(default_factory=list)
    symbols: list[SymbolDef] = field(default_factory=list)

    def with_import(
        self,
        name: str,
        alias: str | None = None,
        module_path: ModuleFqn | None = None,
    ) -> Self:
        self.imports.append(ImportDef(module_path=module_path, name=name, alias=alias))
        return self

    def with_class(self, name: str) -> Self:
        class_def = ClassDef(name=name)
        self.symbols.append(class_def)
        return self

    def with_symbol(self, symbol_def: SymbolDef) -> Self:
        self.symbols.append(symbol_def)
        return self

    def build(self) -> ModuleBlueprint:
        return ModuleBlueprint(
            path=self.path,
            imports=self.imports,
            symbols=self.symbols,
        )
