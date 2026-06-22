from codegen.code_metadata.domain.core.fqn import Fqn
from foundation.building_blocks.event import DomainEvent


class ModuleDefinedClass(DomainEvent):
    module_id: Fqn
    class_id: Fqn
