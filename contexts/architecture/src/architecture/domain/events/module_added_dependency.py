from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.event import DomainEvent


class ModuleAddedDependency(DomainEvent):
    module_id: ModuleId
    target_module_id: ModuleId
    