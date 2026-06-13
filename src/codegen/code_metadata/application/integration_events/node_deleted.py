from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.domain.core.event import IntegrationEvent


class NodeDeletedIntegrationEvent(IntegrationEvent):
    node_id: Fqn
    node_kind: CodeNodeKind
    