from architecture.domain.identities.module_id import ModuleId
from foundation.building_blocks.event import DomainEvent


class ModuleAddedDependency(DomainEvent):
    module_id: ModuleId
    target_module_id: ModuleId
