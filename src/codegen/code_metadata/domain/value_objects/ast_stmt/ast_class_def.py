from __future__ import annotations
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeParam
from foundation.building_blocks.value_object import ValueObject
from pydantic import Field
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt

class AstClassDef(ValueObject):
    kind: Literal[AstStmtKind.CLASS_DEF] = AstStmtKind.CLASS_DEF
    name: str
    description: str | None = None
    bases: list[AstExpr] = Field(default_factory=list)
    keywords: list[AstKeyword] = Field(default_factory=list)
    type_params: list[AstTypeParam] = Field(default_factory=list)
    body: list[AstStmt] = Field(default_factory=list)
    decorator_list: list[AstExpr] = Field(default_factory=list)
