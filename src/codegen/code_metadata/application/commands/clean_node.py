from dataclasses import dataclass

from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    ModuleNode,
)
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command


class CleanNodeCommand(Command):
    fqn: str


@dataclass
class CleanNodeHandler:
    query_service: CodeNodeQueryService

    def execute(
        self, cmd: CleanNodeCommand, uow: UnitOfWork[CodeNodeRepository]
    ) -> None:
        node = uow.repository.get(id=Fqn(cmd.fqn))
        match node:
            case ClassNode():
                unused_nodes = self.query_service.find_unused_nodes(fqns={node.id})
                if not unused_nodes:
                    return
            case ModuleNode():
                empty_modules = self.query_service.find_empty_modules(
                    fqns={node.id}
                )
                if not empty_modules:
                    return
            case _:
                raise NotImplementedError(f"{node.kind=}")

        node.mark_deleted()
        uow.repository.delete(node)
