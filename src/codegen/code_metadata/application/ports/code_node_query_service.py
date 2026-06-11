from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from codegen.code_metadata.application.dtos.code_node_detail_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind


class CodeNodeQueryService(ABC):
    """CodeNode 的 CQRS 读侧端口：直接查询 DTO，不经过领域模型。"""

    @abstractmethod
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNode]:
        """查询 fqn 以指定前缀开头的所有 CodeNode（含根节点自身）。"""
        pass

    @abstractmethod
    def find_by_fqns(
        self, fqns: Collection[str], with_outbounds: bool = False
    ) -> list[CodeNode]:
        """按 FQN 集合批量查询 CodeNode。

        Args:
            fqns: 要查询的 FQN 集合。
            with_outbounds: 若为 True，还会将出边指向的节点一并查出。
        """
        pass

    @abstractmethod
    def find_by_fqn(self, fqn: str) -> CodeNodeDetailDto | None:
        """按 FQN 查询单个 CodeNode 的详情（含入边和出边）。"""
        pass

    @abstractmethod
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        """按 ID 查询单个 CodeNode 的详情（含入边和出边）。"""
        pass

    @abstractmethod
    def find_unused_nodes(
        self,
        kind: CodeNodeKind | None = None,
        fqns: Collection[str] | None = None,
    ) -> list[CodeNode]:
        """查询指定类型下未被使用的节点（支持 CLASS、FUNCTION、VARIABLE）。

        "未被使用"的判定逻辑：不存在类型为 IMPORTS 的入边。
        """
        pass

    @abstractmethod
    def find_all_dead_nodes_cascading(
        self,
        kind: CodeNodeKind,
    ) -> list[CodeNode]:
        ...

    @abstractmethod
    def find_empty_modules(
        self,
        fqns: Collection[Fqn] | None = None,
    ) -> list[CodeNode]:
        """查找没有 DEFINES 出边的 MODULE 节点。

        Args:
            fqns: 可选的 FQN 集合，用于限定搜索范围。
        """
        ...