from foundation.common_types.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn
from foundation.building_blocks.event import DomainEvent


class ModuleCreated(DomainEvent):
    module_id: ModuleId
    module_fqn: ModuleFqn
    is_package: bool
