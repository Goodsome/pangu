from dataclasses import dataclass, field

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.value_objects.ast_stmt_old import (
    AstClassDef,
    AstFunctionDef,
)


@dataclass
class DocumentContext:
    """存储单个代码文档在解析过程中的中间数据"""

    ast_to_node_map: dict[int, CodeNode] = field(default_factory=dict)

    def store(
        self, ast_node: AstClassDef | AstFunctionDef | CodeDocument, node: CodeNode
    ):
        self.ast_to_node_map[id(ast_node)] = node

    def get_node_by_ast(
        self, ast_node: AstClassDef | AstFunctionDef | CodeDocument
    ) -> CodeNode:
        return self.ast_to_node_map[id(ast_node)]
