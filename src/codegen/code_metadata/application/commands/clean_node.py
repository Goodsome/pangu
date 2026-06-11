from dataclasses import dataclass

from pydantic import BaseModel

from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.code_metadata.domain.value_objects.code_edge import DefinesEdge
from codegen.shared.application.ports.unit_of_work import UnitOfWork


class CleanNodeCommand(BaseModel):
    fqn: str


@dataclass
class CleanNodeHandler:
    query_service: CodeNodeQueryService
    uow: UnitOfWork[CodeNodeRepository]

    def execute(self, cmd: CleanNodeCommand) -> None:
        unused_nodes = self.query_service.find_unused_nodes(fqns={cmd.fqn})
        if not unused_nodes:
            return
        module_fqns: set[Fqn] = {node.id.module_fqn for node in unused_nodes}

        with self.uow:
            for node in unused_nodes:
                self.uow.repository.delete(node)
                
            self.uow.commit()
