from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.event import DomainEvent


class ModuleRemovedContains(DomainEvent):
    module_id: ModuleId
    child_module_id: ModuleId
