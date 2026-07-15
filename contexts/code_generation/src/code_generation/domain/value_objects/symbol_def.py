from foundation.building_blocks.value_object import ValueObject
from pydantic import Field


class ClassInheritance(ValueObject):
    name: str
    args: list[str] = Field(default_factory=list)

    def collect_symbols(self) -> set[str]:
        return {self.name} | set(self.args)


class ClassDef(ValueObject):
    name: str
    inherits: list[ClassInheritance]

    def collect_dependencies(self) -> set[str]:
        dependencies: set[str] = set()
        for inheritance in self.inherits:
            dependencies.update(inheritance.collect_symbols())
        return dependencies


class FunctionDef(ValueObject):
    name: str


class VariableDef(ValueObject):
    name: str


SymbolDef = ClassDef | FunctionDef | VariableDef