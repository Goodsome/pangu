from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.domain.enums.edge_kind import EdgeKind
from foundation.building_blocks.value_object import ValueObject


class ParsedEdge(ValueObject):
    kind: EdgeKind
    source: ModuleFqn
    target: ModuleFqn
