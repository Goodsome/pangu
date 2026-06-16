from dataclasses import dataclass
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.domain.core.command import Command


class CleanNodeCommand(Command):
    fqn: str


@dataclass
class CleanNodeHandler:
    query_service: CodeNodeQueryService
    sync_service: CodeNodeSyncService

    def execute(
        self, cmd: CleanNodeCommand, uow: UnitOfWork
    ) -> None:
        fqn = Fqn(cmd.fqn)
        node = uow.repository.get(id=fqn)
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
        uow.repository.delete_by_fqn_prefix(fqn_prefixes={fqn})
        self.sync_service.delete_stale_nodes(fqn_prefixes=[node.id])
