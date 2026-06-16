from dataclasses import dataclass

from codegen.code_metadata.application.commands.delete_module_in_physical import (
    DeleteModuleInPhysicalCommand,
)
from codegen.code_metadata.application.commands.generate_code import GenerateCodeCommand
from codegen.code_metadata.application.unit_of_work import UnitOfWork
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.application.integration_events.node_moved import (
    NodeMovedIntegrationEvent,
)


@dataclass
class OnNodeMoved:
    def regenerate_codes(self, event: NodeMovedIntegrationEvent, uow: UnitOfWork):
        
        yield DeleteModuleInPhysicalCommand(fqns=[event.old_fqn])

        modules_fqns: set[Fqn] = {
            event.new_fqn, 
            event.old_fqn.parent_fqn
        }

        yield GenerateCodeCommand(fqns=list(modules_fqns))
