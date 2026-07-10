from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from foundation.building_blocks.value_object import ValueObject


class AstDelete(ValueObject):
    kind: Literal[AstStmtKind.DELETE] = AstStmtKind.DELETE
    targets: list[AstExpr] = Field(default_factory=list)
