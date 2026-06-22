
from typing import Literal

from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from foundation.building_blocks.value_object import ValueObject


class AstClassDef(ValueObject):
    kind: Literal[AstStmtKind.CLASS_DEF] = AstStmtKind.CLASS_DEF
    name: str
    description: str | None = None
    bases: list[AstExpr] = Field(default_factory=list)
    expr: AstExpr