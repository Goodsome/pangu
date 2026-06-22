from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.domain.enums.edge_kind import EdgeKind
from codegen.shared.domain.core.value_object import ValueObject

class ParsedEdge(ValueObject):
    kind: EdgeKind
    source: ModuleFqn
    target: ModuleFqn