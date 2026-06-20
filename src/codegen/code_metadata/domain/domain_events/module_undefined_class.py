from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.domain.core.event import DomainEvent


class ModuleUndefiedClass(DomainEvent):
    module_id: Fqn
    class_id: Fqn