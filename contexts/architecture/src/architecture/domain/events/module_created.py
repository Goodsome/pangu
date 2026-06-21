from architecture.domain.value_objects.fqn import ModuleFqn
from codegen.shared.domain.core.event import DomainEvent


class ModuleCreated(DomainEvent):
    module_fqn: ModuleFqn
    is_package: bool
    