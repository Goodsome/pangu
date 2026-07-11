from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_type_param import AstTypeParam
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from pydantic import Field
from typing import Literal


class AstClassDef(AstStmtBase):
    kind: Literal[AstStmtKind.CLASS_DEF] = AstStmtKind.CLASS_DEF
    name: str
    description: str | None = None
    bases: list[AstExprBase] = Field(default_factory=list)
    keywords: list[AstKeyword] = Field(default_factory=list)
    type_params: list[AstTypeParam] = Field(default_factory=list)
    body: list[AstStmtBase] = Field(default_factory=list)
    decorator_list: list[AstExprBase] = Field(default_factory=list)
