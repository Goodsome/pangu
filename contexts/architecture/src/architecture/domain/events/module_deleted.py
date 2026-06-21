from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn
from codegen.shared.domain.core.event import DomainEvent


class ModuleDeleted(DomainEvent):
    module_id: ModuleId
    module_fqn: ModuleFqn
    is_package: bool
