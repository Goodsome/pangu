import builtins
from foundation.building_blocks.value_object import ValueObject
from pydantic import Field


class ClassInheritance(ValueObject):
    name: str
    args: list[str] = Field(default_factory=list)

    def collect_symbols(self) -> set[str]:
        symbols = {self.name} | set(self.args)
        return {s for s in symbols if not hasattr(builtins, s)}


class MethodDef(ValueObject):
    name: str
    decorators: list[str] = Field(default_factory=list)
    return_type: str | None = None
    params: list[str] = Field(default_factory=lambda: ["self"])

    def collect_dependencies(self) -> set[str]:
        deps = {d for d in self.decorators if not hasattr(builtins, d)}
        if self.return_type and not hasattr(builtins, self.return_type):
            deps.add(self.return_type)
        return deps


class ClassDef(ValueObject):
    name: str
    inherits: list[ClassInheritance] = Field(default_factory=list)
    methods: list[MethodDef] = Field(default_factory=list)

    def collect_dependencies(self) -> set[str]:
        dependencies: set[str] = set()
        for inheritance in self.inherits:
            dependencies.update(inheritance.collect_symbols())
        for method in self.methods:
            dependencies.update(method.collect_dependencies())
        return dependencies


class FunctionDef(ValueObject):
    name: str


class VariableDef(ValueObject):
    name: str


SymbolDef = ClassDef | FunctionDef | VariableDef