from abc import ABC, abstractmethod

from spike.domain.value_objects.scaffold_payload import ScaffoldPayload


class ScaffoldBuilder(ABC):
    @abstractmethod
    async def build(self, scaffold_payload: ScaffoldPayload) -> str: ...
