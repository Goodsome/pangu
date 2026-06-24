from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from code_dom.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.registry.node_registry import NodeRegistry


class FileDiffer(ABC):
    @abstractmethod
    def get_diff_metric(
        self, module: ModuleNode, node_registry: NodeRegistry
    ) -> FileMetrics: ...
