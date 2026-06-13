from collections.abc import Iterable
from dataclasses import dataclass

from codegen.code_metadata.application.commands.clean_unused_nodes import CleanUnusedNodesCommand
from codegen.code_metadata.application.commands.delete_module_in_physical import DeleteModuleInPhysicalCommand
from codegen.code_metadata.application.dtos.generate_code_command import GenerateCodeCommand
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.application.integration_events.batch_nodes_deleted import (
    BatchNodesDeletedIntegrationEvent,
)
from codegen.shared.domain.core.command import Command


@dataclass
class OnBatchNodesDeleted:
    
    def handle_nodes_deleted(
        self,
        event: BatchNodesDeletedIntegrationEvent,
        uow: UnitOfWork,
    ) -> Iterable[Command]:
        match event.node_kind:
            case CodeNodeKind.CLASS:
                module_fqns = {node_id.module_fqn for node_id in event.node_ids}
                empty_modules = uow.repository.find_empty_modules(fqns=module_fqns)
                empty_module_fqns = {m.id for m in empty_modules}
                if empty_modules:
                    yield CleanUnusedNodesCommand(
                        kind=CodeNodeKind.MODULE,
                    )
                refresh_module_fqns = module_fqns - empty_module_fqns
                if refresh_module_fqns:
                    yield GenerateCodeCommand(fqns=list(refresh_module_fqns))
            case CodeNodeKind.MODULE:
                yield DeleteModuleInPhysicalCommand(fqns=event.node_ids)
            case _:
                raise NotImplementedError(f"{event.node_kind=}")


