from architecture.domain.value_objects.fqn import ModuleFqn
from foundation.building_blocks.event import DomainEvent


class ModuleCreated(DomainEvent):
    module_fqn: ModuleFqn
    is_package: bool
