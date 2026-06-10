from __future__ import annotations
from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class GraphViewNode:
    """依赖图视图的递归树节点。 node 为 None 时表示分组节点（如 "Calls:" 标签），仅用于展示分组标题。"""

    node: CodeNode | None
    edge_type: EdgeType | None = None
    children: list[GraphViewNode] = field(default_factory=list)


@dataclass
class GraphViewDTO:
    """符号依赖追踪的结果 DTO：以目标节点为根的依赖树。"""

    root: GraphViewNode
