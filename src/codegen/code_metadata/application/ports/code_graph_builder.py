from abc import ABC
from abc import abstractmethod
from pathlib import Path
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.registry.node_registry import NodeRegistry


class CodeGraphBuilder(ABC):
    """应用层 Port：从文件系统构建 CodeNode 图。"""

    @abstractmethod
    def get_code_documents(self, module_path: Path) -> list[CodeDocument]:
        """遍历指定上下文的目录树，返回完整的 CodeNode 列表。"""
        ...

    @abstractmethod
    def build_nodes(
        self,
        root_path: Path,
        node_registry: NodeRegistry,
        code_documents: list[CodeDocument],
    ) -> set[str]: ...

    @abstractmethod
    def build_edges(
        self, node_registry: NodeRegistry, code_documents: list[CodeDocument]
    ) -> None: ...
