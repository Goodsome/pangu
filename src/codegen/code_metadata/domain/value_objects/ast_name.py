from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from foundation.building_blocks.value_object import ValueObject


class AstName(ValueObject):
    kind: Literal[AstExprKind.NAME] = AstExprKind.NAME
    id: str
