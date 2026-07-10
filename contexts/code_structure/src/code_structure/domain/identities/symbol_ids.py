from typing import override
from foundation.common_types.identifier import UuidIdentifier


class ClassId(UuidIdentifier):
    
    @override
    def __hash__(self) -> int:
        return hash(self.value)

class FunctionId(UuidIdentifier):
    
    @override
    def __hash__(self) -> int:
        return hash(self.value)


class VariableId(UuidIdentifier):
    
    @override
    def __hash__(self) -> int:
        return hash(self.value)


class MethodId(UuidIdentifier):
    @override
    def __hash__(self) -> int:
        return hash(self.value)


class AttributeId(UuidIdentifier):
    @override
    def __hash__(self) -> int:
        return hash(self.value)


class ExternalSymbolId(UuidIdentifier):
    @override
    def __hash__(self) -> int:
        return hash(self.value)
