from dataclasses import dataclass
from typing import override
from code_dom.application.commands.generate_code import GenerateCodeCommand
from code_dom.application.commands.generate_code import GenerateCodeHandler
from code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.infrastructure.gateways.file_system_file_differ import (
    module_node_dto_to_code_document,
)


@dataclass
class PythonCodeGenerator(CodeGenerator):
    generate_code_handler: GenerateCodeHandler

    @override
    def generate_code_by_nodes(
        self, nodes: list[CodeNode], node_registry: NodeRegistry
    ) -> None:
        code_documents: list[CodeDocument] = []
        for node in nodes:
            if not isinstance(node, ModuleNode):
                continue
            code_document = module_node_dto_to_code_document(node, node_registry)
            code_documents.append(code_document)
        cmd = GenerateCodeCommand(code_documents=code_documents)
        self.generate_code_handler.execute(cmd)
