from __future__ import annotations

from typing import Literal

from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase


class AstSlice(AstExprBase):
    kind: Literal[AstExprKind.SLICE] = AstExprKind.SLICE
    lower: AstExprBase | None = None
    upper: AstExprBase | None = None
    step: AstExprBase | None = None
