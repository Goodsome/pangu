from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from typing import Optional
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAssert(ValueObject):
    kind: Literal[AstStmtKind.ASSERT] = AstStmtKind.ASSERT
    test: AstExpr
    msg: Optional[AstExpr] = None
