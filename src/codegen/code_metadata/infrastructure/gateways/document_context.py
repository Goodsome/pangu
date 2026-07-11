from dataclasses import dataclass, field
from code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_stmt import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)


@dataclass
class DocumentContext:
    """存储单个代码文档在解析过程中的中间数据"""

    "存储单个代码文档在解析过程中的中间数据"
    ast_to_node_map: dict[int, CodeNode] = field(default_factory=dict)

    def store(
        self,
        ast_node: AstClassDef
        | AstFunctionDef
        | CodeDocument
        | AstAnnAssign
        | AstAssign,
        node: CodeNode,
    ):
        self.ast_to_node_map[id(ast_node)] = node

    def get_node_by_ast(
        self,
        ast_node: AstClassDef
        | AstFunctionDef
        | CodeDocument
        | AstAnnAssign
        | AstAssign,
    ) -> CodeNode:
        return self.ast_to_node_map[id(ast_node)]
