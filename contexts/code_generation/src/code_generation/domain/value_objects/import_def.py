from foundation.building_blocks.value_object import ValueObject
from foundation.common_types.fqns.fqn import ModuleFqn


class ImportDef(ValueObject):
    name: str
    alias: str | None
    module_path: ModuleFqn | None = None