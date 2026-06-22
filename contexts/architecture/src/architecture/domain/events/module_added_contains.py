from architecture.domain.identities.module_id import ModuleId
from foundation.building_blocks.event import DomainEvent


class ModuleAddedContains(DomainEvent):
    module_id: ModuleId
    child_module_id: ModuleId
