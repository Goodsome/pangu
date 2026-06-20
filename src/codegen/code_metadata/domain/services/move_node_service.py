
from dataclasses import dataclass

from codegen.code_metadata.domain.aggregates import ClassNode, CodeNode, ModuleNode


@dataclass
class MoveNodeService:
    def move(
        self,
        node: CodeNode,
        source_node: CodeNode,
        target_node: CodeNode,
    ):
        match node, source_node, target_node:
            case ClassNode(), ModuleNode(), ModuleNode():
                target_node.defines_v2(node.id)
                source_node.undefines(node.id)
                node.moved(from_=source_node.id, to=target_node.id)
            case _:
                raise NotImplementedError()
