from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstExprStmt(ValueObject):
    kind: Literal[AstStmtKind.EXPR_STMT] = AstStmtKind.EXPR_STMT
    value: AstExpr
