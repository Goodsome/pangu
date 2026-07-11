from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstAssign(AstStmtBase):
    kind: Literal[AstStmtKind.ASSIGN] = AstStmtKind.ASSIGN
    targets: list[AstExprBase] = Field(default_factory=list)
    value: AstExprBase | None

    @property
    def target(self):
        if len(self.targets) != 1:
            raise ValueError(f"targets must have exactly one element: self={self!r}")
        return self.targets[0]

    @property
    def annotation(self) -> None:
        return
