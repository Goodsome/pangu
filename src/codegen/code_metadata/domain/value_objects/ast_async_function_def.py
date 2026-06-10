from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
    from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
    from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeParam


class AstAsyncFunctionDef(ValueObject):
    kind: Literal[AstStmtKind.ASYNC_FUNCTION_DEF] = AstStmtKind.ASYNC_FUNCTION_DEF
    name: str
    type_params: list[AstTypeParam] = Field(default_factory=list)
    args: AstArguments
    body: list[AstStmt] = Field(default_factory=list)
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
    type_comment: str | None = None
