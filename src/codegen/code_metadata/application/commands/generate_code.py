from dataclasses import dataclass
from codegen.code_metadata.application.dtos.generate_code_command import (
    GenerateCodeCommand,
)
from codegen.code_metadata.application.dtos.generate_code_result import (
    GenerateCodeResult,
)
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator


@dataclass
class GenerateCode:
    query_service: CodeNodeQueryService
    code_generator: CodeGenerator

    def execute(self, cmd: GenerateCodeCommand) -> GenerateCodeResult:
        nodes = self.query_service.find_by_fqn_prefix(cmd.fqn)
        registry = NodeRegistry.create(nodes=nodes)
        self.code_generator.generate_code_by_nodes(nodes=nodes, node_registry=registry)
        return GenerateCodeResult(code="success")
