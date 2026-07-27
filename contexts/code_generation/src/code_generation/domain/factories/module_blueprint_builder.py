from dataclasses import dataclass, field
from typing import Self

from foundation.common_types.fqns.fqn import ModuleFqn

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.value_objects.import_def import ImportDef
from code_generation.domain.value_objects.symbol_def import (
    ClassDef,
    ClassInheritance,
    FunctionDef,
    MethodDef,
    ParamDef,
    StmtDef,
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
        inherits: list[ClassInheritance] | None = None,
        methods: list[MethodDef] | None = None,
        decorators: list[str] | None = None,
    ) -> Self:
        class_def = ClassDef(
            name=name,
            decorators=decorators or [],
            inherits=inherits or [],
            methods=methods or [],
        )
        return self.with_symbol(class_def)

    def with_function(
        self,
        name: str,
        params: list[ParamDef] | None = None,
        return_type: str | None = None,
        decorators: list[str] | None = None,
        body: list[StmtDef] | None = None,
    ) -> Self:
        func_def = FunctionDef(
            name=name,
            decorators=decorators or [],
            return_type=return_type,
            params=params or [],
            body=body or [],
        )
        return self.with_symbol(func_def)

    def with_symbol(self, symbol_def: SymbolDef) -> Self:
        self.symbols.append(symbol_def)
        for dependency in symbol_def.collect_dependencies():
            self.with_import(name=dependency)
        return self

    def build(self) -> ModuleBlueprint:
        return ModuleBlueprint(
            path=self.path,
            imports=list(self.imports.values()),
            symbols=self.symbols,
        )
