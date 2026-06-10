from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.application.dtos.bulk_save_result import BulkSaveResult
from codegen.code_metadata.domain.aggregates.code_node import CodeNode


class CodeNodeSyncService(ABC):
    """应用层 Port：批量同步 CodeNode 图。"""

    @abstractmethod
    def save_nodes_bulk(
        self, node_dtos: list[CodeNode], sync_id: str, fqn_prefix: str
    ) -> BulkSaveResult: ...

    @abstractmethod
    def delete_stale_nodes(self, fqn_prefix: str, current_sync_id: str) -> int: ...
