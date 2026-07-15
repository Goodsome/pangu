from foundation.building_blocks.value_object import ValueObject

class ClassDef(ValueObject):
    name: str


class FunctionDef(ValueObject):
    name: str


class VariableDef(ValueObject):
    name: str


SymbolDef = ClassDef | FunctionDef | VariableDef