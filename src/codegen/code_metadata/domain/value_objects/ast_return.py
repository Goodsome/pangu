from __future__ import annotations
from typing import Literal
from typing import Optional
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstReturn(ValueObject):
    kind: Literal[AstStmtKind.RETURN] = AstStmtKind.RETURN
    value: Optional[AstExpr] = None
