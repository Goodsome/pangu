import builtins
from foundation.building_blocks.value_object import ValueObject
from pydantic import Field


class ClassInheritance(ValueObject):
    name: str
    args: list[str] = Field(default_factory=list)

    def collect_symbols(self) -> set[str]:
        symbols = {self.name} | set(self.args)
        return {s for s in symbols if not hasattr(builtins, s)}


class PassDef(ValueObject):
    pass


class RawStmtDef(ValueObject):
    code: str


StmtDef = PassDef | RawStmtDef


class ParamDef(ValueObject):
    name: str
    type_annotation: str | None = None

    def collect_symbols(self) -> set[str]:
        if self.type_annotation and not hasattr(builtins, self.type_annotation):
            return {self.type_annotation}
        return set()


class MethodDef(ValueObject):
    name: str
    decorators: list[str] = Field(default_factory=list)
    return_type: str | None = None
    params: list[ParamDef] = Field(default_factory=lambda: [ParamDef(name="self")])
    body: list[StmtDef] = Field(default_factory=lambda: [PassDef()])

    def collect_dependencies(self) -> set[str]:
        deps = {d for d in self.decorators if not hasattr(builtins, d)}
        if self.return_type and not hasattr(builtins, self.return_type):
            deps.add(self.return_type)
        for param in self.params:
            deps.update(param.collect_symbols())
        return deps


class ClassDef(ValueObject):
    name: str
    decorators: list[str] = Field(default_factory=list)
    inherits: list[ClassInheritance] = Field(default_factory=list)
    methods: list[MethodDef] = Field(default_factory=list)

    def collect_dependencies(self) -> set[str]:
        dependencies: set[str] = {d for d in self.decorators if not hasattr(builtins, d)}
        for inheritance in self.inherits:
            dependencies.update(inheritance.collect_symbols())
        for method in self.methods:
            dependencies.update(method.collect_dependencies())
        return dependencies


class FunctionDef(ValueObject):
    name: str
    decorators: list[str] = Field(default_factory=list)
    return_type: str | None = None
    params: list[ParamDef] = Field(default_factory=list)
    body: list[StmtDef] = Field(default_factory=lambda: [PassDef()])

    def collect_dependencies(self) -> set[str]:
        deps = {d for d in self.decorators if not hasattr(builtins, d)}
        if self.return_type and not hasattr(builtins, self.return_type):
            deps.add(self.return_type)
        for param in self.params:
            deps.update(param.collect_symbols())
        return deps


class VariableDef(ValueObject):
    name: str

    def collect_dependencies(self) -> set[str]:
        return set()


SymbolDef = ClassDef | FunctionDef | VariableDef