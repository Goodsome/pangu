from dataclasses import dataclass
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command


class CleanNodeCommand(Command):
    fqn: str


@dataclass
class CleanNodeHandler:
    query_service: CodeNodeQueryService
    sync_service: CodeNodeSyncService

    def execute(
        self, cmd: CleanNodeCommand, uow: UnitOfWork[CodeNodeRepository]
    ) -> None:
        node = uow.repository.get(id=Fqn(cmd.fqn))
        match node:
            case ModuleNode():
                empty_modules = self.query_service.find_empty_modules(fqns={node.id})
                if not empty_modules:
                    return
            case _:
                unused_nodes = self.query_service.find_unused_nodes(fqns={node.id})
                if not unused_nodes:
                    return
        node.mark_deleted()
        uow.repository.delete(node)
        self.sync_service.delete_stale_nodes(fqn_prefixes=[node.id])
