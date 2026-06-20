from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.domain.core.event import DomainEvent


class ClassRemoved(DomainEvent):
    class_id: Fqn
    from_module_id: Fqn
    to_module_id: Fqn
    