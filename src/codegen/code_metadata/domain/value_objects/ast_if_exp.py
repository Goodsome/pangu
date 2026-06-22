from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from foundation.building_blocks.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstIfExp(ValueObject):
    kind: Literal[AstExprKind.IF_EXP] = AstExprKind.IF_EXP
    test: AstExpr
    body: AstExpr
    orelse: AstExpr
