from typing import override
from foundation.common_types.identifier import UuidIdentifier


class ModuleId(UuidIdentifier):
    @override
    def __hash__(self) -> int:
        return hash(self.value)
