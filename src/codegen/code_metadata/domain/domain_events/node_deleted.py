from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from foundation.building_blocks.event import DomainEvent


class NodeDeleted(DomainEvent):
    node_id: Fqn
    node_kind: CodeNodeKind
