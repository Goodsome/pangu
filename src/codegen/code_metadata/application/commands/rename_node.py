from dataclasses import dataclass
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.application.integration_events.node_moved import (
    NodeMovedIntegrationEvent,
)
from foundation.building_blocks.command import Command


class RenameNodeCommand(Command):
    fqn: Fqn
    name: str


@dataclass
class RenameNodeHandler:
    def execute(self, cmd: RenameNodeCommand, uow: UnitOfWork):
        if cmd.fqn.symbol == cmd.name:
            return
        new_fqn = uow.repository.rename_node(node_fqn=cmd.fqn, new_name=cmd.name)
        event = NodeMovedIntegrationEvent(old_fqn=cmd.fqn, new_fqn=new_fqn)
        uow.save_outbox_message(event)
