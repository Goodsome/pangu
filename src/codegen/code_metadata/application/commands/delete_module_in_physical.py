import logging
from dataclasses import dataclass
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command
from codegen.shared.domain.ports.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)

class DeleteModuleInPhysicalCommand(Command):
    fqns: list[Fqn]


@dataclass
class DeleteModuleInPhysicalHandler:
    file_system: FileSystemPort

    def execute(self, cmd: DeleteModuleInPhysicalCommand, uow: UnitOfWork[CodeNodeRepository]):
        for fqn in cmd.fqns:
            module_path = FqnFactory.fqn_to_path(fqn)
            if module_path.with_suffix(".py").is_file():
                self.file_system.delete_file(module_path)
            else:
                logger.info(f"{module_path=} is not file")
            
    