from pydantic import BaseModel
from architecture.domain.value_objects.fqn import ModuleFqn


class ModuleDto(BaseModel):
    fqn: ModuleFqn
    name: str
    is_package: bool