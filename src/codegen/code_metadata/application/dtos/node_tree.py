from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.code_node import CodeNode


@dataclass
class NodeTree:
    """目录树节点：递归结构，每个节点持有 CodeNode 及其子树。"""

    node: CodeNode
    children: list["NodeTree"] = field(default_factory=list)
