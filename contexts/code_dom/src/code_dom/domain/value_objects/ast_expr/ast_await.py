from __future__ import annotations
from typing import Literal
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase


class AstAwait(AstExprBase):
    kind: Literal[AstExprKind.AWAIT] = AstExprKind.AWAIT
    value: AstExprBase
