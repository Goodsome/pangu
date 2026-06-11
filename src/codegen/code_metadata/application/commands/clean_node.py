from dataclasses import dataclass
from pydantic import BaseModel

from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService


class CleanNodeCommand(BaseModel):
    fqn: str


@dataclass
class CleanNodeHandler:
    query_service: CodeNodeQueryService

    def execute(self, cmd: CleanNodeCommand) -> None:
        node = self.query_service.find_unused_nodes(
            
        )
        if node is None:
            return
        