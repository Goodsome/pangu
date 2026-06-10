import ast
from dataclasses import dataclass
from typing import override
from codegen.code_dom.application.commands.generate_code import GenerateCodeCommand
from codegen.code_dom.application.commands.generate_code import GenerateCodeHandler
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.services.translate_reference import TranslateReference
from codegen.code_metadata.infrastructure.gateways.file_system_file_differ import (
    module_node_dto_to_code_document,
)
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import (
    ComponentToAstModule,
)


@dataclass
class PythonCodeGenerator(CodeGenerator):
    component_policy_factory: ComponentPolicyFactory
    generate_code_handler: GenerateCodeHandler

    @override
    def generate(self, component: Component, resolver: TranslateReference) -> str:
        mapper = ComponentToAstModule(
            resolver=resolver, component_policy_factory=self.component_policy_factory
        )
        module = mapper.to_ast_module(component)
        ast.fix_missing_locations(module)
        return ast.unparse(module)

    @override
    def generate_module_code(
        self, module: FileModule, resolver: TranslateReference
    ) -> str:
        mapper = ComponentToAstModule(
            resolver=resolver, component_policy_factory=self.component_policy_factory
        )
        ast_module = mapper.module_to_ast(module)
        ast.fix_missing_locations(ast_module)
        return ast.unparse(ast_module)

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
