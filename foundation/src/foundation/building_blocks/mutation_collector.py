from pydantic.config import ConfigDict
from typing_extensions import ClassVar
from pydantic import BaseModel, PrivateAttr

class Mutation(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    

class MutationCollector(BaseModel):

    _mutations: list[Mutation] = PrivateAttr(default_factory=list)

    def add_mutation(self, mutation: Mutation):
        self._mutations.append(mutation)

    def collect_mutations(self) -> list[Mutation]:
        mutations = self._mutations.copy()
        self._mutations.clear()
        return mutations
        
    