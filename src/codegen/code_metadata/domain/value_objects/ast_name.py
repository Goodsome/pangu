from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.shared.domain.core.value_object import ValueObject


class AstName(ValueObject):
    kind: Literal[AstExprKind.NAME] = AstExprKind.NAME
    id: str
