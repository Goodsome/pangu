from collections.abc import Iterable
from dataclasses import dataclass

from codegen.code_metadata.application.commands.clean_node import (
    CleanNodeCommand,
)
from codegen.code_metadata.application.commands.delete_module_in_physical import (
    DeleteModuleInPhysicalCommand,
)
from codegen.code_metadata.application.dtos.generate_code_command import (
    GenerateCodeCommand,
)
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.domain_events.node_deleted import NodeDeleted
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.application.integration_events.node_deleted import (
    NodeDeletedIntegrationEvent,
)
from codegen.shared.domain.core.command import Command


@dataclass
class OnNodeDeleted:
    def send_to_outbox(
        self,
        event: NodeDeleted,
        uow: UnitOfWork,
    ) -> Iterable[Command]:
        integration_event = NodeDeletedIntegrationEvent(
            node_id=event.node_id,
            node_kind=event.node_kind,
        )
        uow.save_outbox_message(integration_event)
        yield from []

    def handle_clean_node(
        self,
        event: NodeDeletedIntegrationEvent,
        uow: UnitOfWork,
    ) -> Iterable[Command]:
        match event.node_kind:
            case CodeNodeKind.CLASS:
                module_fqn = event.node_id.module_fqn
                empty_modules = uow.repository.find_empty_modules(fqns={module_fqn})
                if empty_modules:
                    yield CleanNodeCommand(fqn=module_fqn)
                else:
                    yield GenerateCodeCommand(fqns=[module_fqn])
            case CodeNodeKind.MODULE:
                yield DeleteModuleInPhysicalCommand(fqns=[event.node_id])
            case _:
                raise NotImplementedError(f"{event.node_kind=}")
