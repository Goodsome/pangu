from dataclasses import dataclass
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.application.integration_events.batch_nodes_deleted import (
    BatchNodesDeletedIntegrationEvent,
)
from codegen.shared.domain.core.command import Command


class CleanUnusedNodesCommand(Command):
    kind: CodeNodeKind
    fqns: list[Fqn] | None = None


@dataclass
class CleanUnusedNodesHandler:
    query_service: CodeNodeQueryService
    sync_service: CodeNodeSyncService

    def execute(self, cmd: CleanUnusedNodesCommand, uow: UnitOfWork):
        match cmd.kind:
            case CodeNodeKind.MODULE:
                nodes = self.query_service.find_empty_modules(fqns=cmd.fqns)
            case _:
                nodes = self.query_service.find_unused_nodes(
                    kind=cmd.kind, fqns=cmd.fqns
                )
        if not nodes:
            return
        clean_node_ids = [n.id for n in nodes]
        self.sync_service.delete_stale_nodes(fqn_prefixes=clean_node_ids)
        event = BatchNodesDeletedIntegrationEvent(
            node_ids=[n.id for n in nodes], node_kind=cmd.kind
        )
        uow.save_outbox_message(event)
