from dataclasses import dataclass
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class DeleteModuleInPhysicalCommand(Command):
    fqn: Fqn


@dataclass
class DeleteModuleInPhysicalHandler:
    file_system: FileSystemPort

    def execute(self, cmd: DeleteModuleInPhysicalCommand, uow: UnitOfWork[CodeNodeRepository]):
        module = uow.repository.get(cmd.fqn)
        if not isinstance(module, ModuleNode):
            raise ValueError(f"{module=} is not ModuleNode")
        module_path = module.get_physical_path()
        if module_path.is_file():
            self.file_system.delete_file(module_path)
            
    