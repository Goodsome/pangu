from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstMatch(ValueObject):
    kind: Literal[AstStmtKind.MATCH] = AstStmtKind.MATCH
    subject: AstExpr
    cases: list[AstMatchCase] = Field(default_factory=list)
