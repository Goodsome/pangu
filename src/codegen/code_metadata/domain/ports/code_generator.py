from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.services.translate_reference import TranslateReference


class CodeGenerator(ABC):

    @abstractmethod
    def generate(self, component: Component, resolver: TranslateReference) -> str: ...

    @abstractmethod
    def generate_module_code(
        self, module: FileModule, resolver: TranslateReference
    ) -> str: ...

    @abstractmethod
    def generate_code_by_nodes(
        self, nodes: list[CodeNode], node_registry: NodeRegistry
    ) -> None: ...
