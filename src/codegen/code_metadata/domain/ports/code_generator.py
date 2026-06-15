from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import CodeNode


class CodeGenerator(ABC):

    @abstractmethod
    def generate_code_by_nodes(
        self, nodes: list[CodeNode], node_registry: NodeRegistry
    ) -> None: ...
