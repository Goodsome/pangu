from dataclasses import dataclass
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.services.move_node_service import MoveNodeService
from foundation.building_blocks.command import Command


class MoveNodeCommand(Command):
    node_fqn: Fqn
    target_fqn: Fqn


@dataclass
class MoveNodeHandler:
    move_node_serivce: MoveNodeService

    def execute(self, cmd: MoveNodeCommand, uow: UnitOfWork):
        if cmd.node_fqn.parent_fqn == cmd.target_fqn:
            return
        node = uow.repository.get(cmd.node_fqn)
        source_node = uow.repository.get(cmd.node_fqn.parent_fqn)
        target_node = uow.repository.get(cmd.target_fqn)
        self.move_node_serivce.move(
            node=node, source_node=source_node, target_node=target_node
        )
        uow.repository.save(node)
        uow.repository.save(source_node)
        uow.repository.save(target_node)
