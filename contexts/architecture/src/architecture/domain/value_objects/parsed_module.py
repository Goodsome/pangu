from pydantic import BaseModel
from foundation.common_types.fqns.fqn import ModuleFqn


class ParsedModule(BaseModel):
    import_module_fqns: list[ModuleFqn]
    fqn: ModuleFqn
    is_package: bool
    is_deleted: bool = False
