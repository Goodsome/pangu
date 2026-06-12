from dataclasses import dataclass
from pathlib import Path
from typing import override
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
)
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.infrastructure.gateways.module_build_context import (
    ModuleBuildContext,
)
from codegen.code_metadata.infrastructure.gateways.node_building_visitor import NodeBuilder


@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。"""

    get_project_documents: GetProjectDocumentsHandler

    @override
    def get_code_documents(self, module_path: Path) -> list[CodeDocument]:
        query = GetProjectDocumentsQuery(dir_path=module_path)
        result = self.get_project_documents.handle(query)
        return result.code_documents

    @override
    def build_nodes(
        self,
        root_path: Path,
        node_registry: NodeRegistry,
        code_documents: list[CodeDocument],
    ) -> set[str]:
        acl = NodeBuilder(
            root_path=root_path, fqn_factory=FqnFactory(), node_registery=node_registry
        )
        acl.build(code_documents)
        return acl.imports

    @override
    def build_edges(
        self, node_registry: NodeRegistry, code_documents: list[CodeDocument]
    ) -> None:
        fqn_factory = FqnFactory()
        for code_document in code_documents:
            if not code_document.is_init_file:
                continue
            module_fqn = fqn_factory.build_module_fqn(code_document.physical_path)
            module = node_registry.get_node(module_fqn)
            assert isinstance(module, ModuleNode)
            module_builder = ModuleBuildContext(module, code_document, node_registry)
            module_builder.build()
        for code_document in code_documents:
            if code_document.is_init_file:
                continue
            module_fqn = fqn_factory.build_module_fqn(code_document.physical_path)
            module = node_registry.get_node(module_fqn)
            assert isinstance(module, ModuleNode)
            module_builder = ModuleBuildContext(module, code_document, node_registry)
            module_builder.build()

