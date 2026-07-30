from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from pydantic import BaseModel


class SymbolDto(BaseModel):
    name: str
    fqn: SymbolFqn

    @property
    def module_fqn(self) -> ModuleFqn:
        return self.fqn.module_fqn
