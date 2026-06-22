from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.lambda_args import LambdaArgs
from foundation.building_blocks.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstLambda(ValueObject):
    kind: Literal[AstExprKind.LAMBDA] = AstExprKind.LAMBDA
    args: LambdaArgs
    body: AstExpr
