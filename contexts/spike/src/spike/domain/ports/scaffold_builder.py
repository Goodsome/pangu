from abc import ABC, abstractmethod

from spike.domain.enums.context_name import ContextName
from spike.domain.enums.scaffold_type import ScaffoldType


class ScaffoldBuilder(ABC):
    @abstractmethod
    async def build(
        self,
        scaffold_type: ScaffoldType,
        context: ContextName,
        description: str,
    ) -> str: ...
