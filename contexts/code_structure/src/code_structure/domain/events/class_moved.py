from foundation.building_blocks.event import DomainEvent
from foundation.common_types.fqns.fqn import ClassFqn
from code_structure.domain.identities.symbol_ids import ClassId


class ClassMoved(DomainEvent):
    class_id: ClassId
    old_fqn: ClassFqn
    new_fqn: ClassFqn
