from typing import ClassVar
from codegen.code_metadata.domain.core.fqn import Fqn
from foundation.building_blocks.event import IntegrationEvent


class NodeMovedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "code_node"
    old_fqn: Fqn
    new_fqn: Fqn
