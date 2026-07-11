from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.event import DomainEvent


class PackageModuleDeleted(DomainEvent):
    module_id: ModuleId
    module_fqn: ModuleFqn
