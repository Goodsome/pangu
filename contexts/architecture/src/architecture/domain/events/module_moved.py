from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn
from codegen.shared.domain.core.event import DomainEvent


class ModuleMoved(DomainEvent):
    module_id: ModuleId
    old_fqn: ModuleFqn
    new_fqn: ModuleFqn
