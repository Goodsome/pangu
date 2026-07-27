from dataclasses import dataclass, field
from typing import Self

from foundation.common_types.fqns.fqn import ModuleFqn

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.value_objects.import_def import ImportDef
from code_generation.domain.value_objects.symbol_def import (
    ClassDef,
    ClassInheritance,
    MethodDef,
    SymbolDef,
)


@dataclass
class ModuleBlueprintBuilder:
    path: ModuleFqn
    imports: dict[str, ImportDef] = field(default_factory=dict)
    symbols: list[SymbolDef] = field(default_factory=list)

    def with_import(
        self,
        name: str,
        alias: str | None = None,
        module_path: ModuleFqn | None = None,
    ) -> Self:
        if name in self.imports:
            return self
        self.imports[name] = ImportDef(module_path=module_path, name=name, alias=alias)
        return self

    def with_class(
        self,
        name: str,
        inherits: list[ClassInheritance],
        methods: list[MethodDef] | None = None,
    ) -> Self:
        class_def = ClassDef(
            name=name,
            inherits=inherits,
            methods=methods or [],
        )
        self.symbols.append(class_def)
        for dependency in class_def.collect_dependencies():
            self.with_import(name=dependency)
        return self

    def with_symbol(self, symbol_def: SymbolDef) -> Self:
        self.symbols.append(symbol_def)
        return self

    def build(self) -> ModuleBlueprint:
        return ModuleBlueprint(
            path=self.path,
            imports=list(self.imports.values()),
            symbols=self.symbols,
        )
