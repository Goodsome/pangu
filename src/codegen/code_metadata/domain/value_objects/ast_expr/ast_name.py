from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase


class AstName(AstExprBase):
    kind: Literal[AstExprKind.NAME] = AstExprKind.NAME
    id: str
