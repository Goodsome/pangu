from dataclasses import dataclass

from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.application.integration_events.batch_nodes_deleted import BatchNodesDeletedIntegrationEvent
from codegen.shared.domain.core.command import Command



class CleanUnusedNodesCommand(Command):
    kind: CodeNodeKind


@dataclass
class CleanUnusedNodesHandler:

    def execute(self, cmd: CleanUnusedNodesCommand, uow: UnitOfWork):
        match cmd.kind:
            case CodeNodeKind.CLASS:
                nodes = uow.repository.find_unused_nodes(
                    kind=CodeNodeKind.CLASS,
                )
            case CodeNodeKind.MODULE:
                nodes = uow.repository.find_empty_modules()
            case _:
                raise NotImplementedError(f"{cmd.kind=}")
                
        if not nodes:
            return
        for node in nodes:
            uow.repository.delete(node)

        event = BatchNodesDeletedIntegrationEvent(
            node_ids=[n.id for n in nodes],
            node_kind=cmd.kind,
        )
        uow.save_outbox_message(event)