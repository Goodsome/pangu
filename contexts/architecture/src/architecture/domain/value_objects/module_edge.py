from architecture.domain.identities.module_id import ModuleId
from foundation.building_blocks.value_object import ValueObject


class DependsOnEdge(ValueObject):
    source: ModuleId
    target: ModuleId
