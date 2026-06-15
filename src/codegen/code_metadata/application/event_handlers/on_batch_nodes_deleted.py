from collections.abc import Iterable
from dataclasses import dataclass

from codegen.code_metadata.application.commands.clean_unused_nodes import CleanUnusedNodesCommand
from codegen.code_metadata.application.commands.delete_module_in_physical import DeleteModuleInPhysicalCommand
from codegen.code_metadata.application.commands.generate_code import GenerateCodeCommand
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
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
            case CodeNodeKind.CLASS | CodeNodeKind.FUNCTION:
                module_fqns = {node_id.module_fqn for node_id in event.node_ids}
                empty_modules = uow.repository.find_empty_modules(fqns=module_fqns)
                empty_module_fqns = {m.id for m in empty_modules}
                if empty_modules:
                    yield CleanUnusedNodesCommand(
                        kind=CodeNodeKind.MODULE,
                        fqns=list(empty_module_fqns),
                    )
                refresh_module_fqns = module_fqns - empty_module_fqns
                package_modules: set[Fqn] = set()
                for module_fqn in module_fqns:
                    parent_fqn = module_fqn.parent_fqn
                    if not parent_fqn:
                        return
                    package_modules.add(parent_fqn)
                
                refresh_module_fqns.update(package_modules)
                if refresh_module_fqns:
                    yield GenerateCodeCommand(fqns=list(refresh_module_fqns))
            case CodeNodeKind.MODULE:
                yield DeleteModuleInPhysicalCommand(fqns=event.node_ids)
            case CodeNodeKind.EXTERNAL:
                pass
            case CodeNodeKind.METHOD | CodeNodeKind.VARIABLE:
                module_fqns = {node_id.module_fqn for node_id in event.node_ids}
                yield GenerateCodeCommand(fqns=list(module_fqns))
            case _:
                pass


