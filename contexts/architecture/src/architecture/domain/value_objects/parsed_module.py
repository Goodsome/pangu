from pydantic import BaseModel

from architecture.domain.value_objects.fqn import ModuleFqn


class ParsedModule(BaseModel):
    import_module_fqns: list[ModuleFqn]
    fqn: ModuleFqn
    is_package: bool
