from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstDelete(AstStmtBase):
    kind: Literal[AstStmtKind.DELETE] = AstStmtKind.DELETE
    targets: list[AstExpr] = Field(default_factory=list)
