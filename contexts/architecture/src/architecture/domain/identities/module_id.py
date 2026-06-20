from typing import override
from codegen.shared.domain.value_objects.identifier import UuidIdentifier


class ModuleId(UuidIdentifier):
    
    @override
    def __hash__(self) -> int:
        return hash(self.value)
        
    