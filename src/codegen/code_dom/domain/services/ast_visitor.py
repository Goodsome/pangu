
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


class AstVisitor:

    def visit(self, node: AstStmt | AstExpr | list[AstExpr] | list[AstStmt]):
        match node:
            case AstClassDef():
                self.visit_ast_class_def(node)
            case list():
                for item in node:
                    self.visit(item)
            case _:
                raise NotImplementedError(f"{node=}")

    def visit_ast_class_def(self, node: AstClassDef):
        self.visit(node.bases)
        self.visit(node.body)
        self.visit(node.decorator_list)