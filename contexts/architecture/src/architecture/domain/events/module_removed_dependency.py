from foundation.common_types.identities.module_id import ModuleId
from foundation.building_blocks.event import DomainEvent


class ModuleRemovedDependency(DomainEvent):
    module_id: ModuleId
    target_module_id: ModuleId
