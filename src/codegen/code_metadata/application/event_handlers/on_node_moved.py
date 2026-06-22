from dataclasses import dataclass
from codegen.code_metadata.application.commands.clean_node import CleanNodeCommand
from codegen.code_metadata.application.commands.delete_module_in_physical import (
    DeleteModuleInPhysicalCommand,
)
from codegen.code_metadata.application.commands.generate_code import GenerateCodeCommand
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from foundation.integration_events.node_moved import NodeMovedIntegrationEvent


@dataclass
class OnNodeMoved:
    def regenerate_codes(self, event: NodeMovedIntegrationEvent, uow: UnitOfWork):
        modules_fqns: set[Fqn] = {event.new_fqn.module_fqn}
        if event.old_fqn.is_module:
            yield DeleteModuleInPhysicalCommand(fqns=[event.old_fqn])
        else:
            old_module_fqn = event.old_fqn.module_fqn
            empty_modules = uow.repository.find_empty_modules(fqns={old_module_fqn})
            if empty_modules:
                yield CleanNodeCommand(fqn=old_module_fqn)
            else:
                yield GenerateCodeCommand(fqns=[old_module_fqn])
        edges = uow.repository.find_edges(
            edge_types=(EdgeType.EXPORTS, EdgeType.IMPORTS),
            target_fqn_prefixes={event.new_fqn},
        )
        for edge in edges:
            modules_fqns.add(edge.source_id)
        yield GenerateCodeCommand(fqns=list(modules_fqns))
