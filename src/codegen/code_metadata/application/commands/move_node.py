from dataclasses import dataclass
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.application.integration_events.node_moved import NodeMovedIntegrationEvent
from codegen.shared.domain.core.command import Command


class MoveNodeCommand(Command):
    node_fqn: Fqn
    target_fqn: Fqn


@dataclass
class MoveNodeHandler:

    def execute(self, cmd: MoveNodeCommand, uow: UnitOfWork):
        if cmd.node_fqn.parent_fqn == cmd.target_fqn:
            return
        new_fqn = uow.repository.move_node(
            node_fqn=cmd.node_fqn,
            target_fqn=cmd.target_fqn
        )
        event = NodeMovedIntegrationEvent(
            old_fqn=cmd.node_fqn,
            new_fqn=new_fqn
        )
        uow.save_outbox_message(event)