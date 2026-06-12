from collections.abc import Iterable
from dataclasses import dataclass

from codegen.code_metadata.application.commands.clean_node import (
    CleanNodeCommand,
)
from codegen.code_metadata.application.commands.delete_module_in_physical import DeleteModuleInPhysicalCommand
from codegen.code_metadata.application.dtos.generate_code_command import GenerateCodeCommand
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.events.node_deleted import NodeDeleted
from codegen.shared.domain.core.command import Command


@dataclass
class OnNodeDeleted:
    query_service: CodeNodeQueryService

    def handle_clean_node(self, event: NodeDeleted) -> Iterable[Command]:
        match event.node_kind:
            case CodeNodeKind.CLASS:
                module_fqn = event.node_id.module_fqn
                empty_modules = self.query_service.find_empty_modules(fqns={module_fqn})
                if empty_modules:
                    yield CleanNodeCommand(fqn=module_fqn)
                else:
                    yield GenerateCodeCommand(fqn=module_fqn)
            case CodeNodeKind.MODULE:
                yield DeleteModuleInPhysicalCommand(fqn=event.node_id)
            case _:
                raise NotImplementedError(f"{event.node_kind=}")
