from dataclasses import dataclass
from pydantic import BaseModel

from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class SyncModuleCommand(BaseModel):
    module_fqn: str


@dataclass
class SyncModuleHandler:
    query_service: CodeNodeQueryService
    code_generator: CodeGenerator
    file_system: FileSystemPort

    def execute(self, cmd: SyncModuleCommand) -> None:
        fqn = Fqn(cmd.module_fqn)
        empty_modules = self.query_service.find_empty_modules(
            fqns={fqn}
        )
        if not empty_modules:
            nodes = self.query_service.find_by_fqn_prefix(str(cmd.module_fqn))
            registry = NodeRegistry.create(nodes=nodes)
            self.code_generator.generate_code_by_nodes(nodes=nodes, node_registry=registry)
            return
            
        for module in empty_modules:
            assert isinstance(module, ModuleNode)
            self.file_system.delete_file(
                path=module.get_physical_path()
            )
            
        