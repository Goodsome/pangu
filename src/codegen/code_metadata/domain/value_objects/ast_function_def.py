from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
    from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
    from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeParam


class AstFunctionDef(ValueObject):
    lineno: int
    kind: Literal[AstStmtKind.FUNCTION_DEF] = AstStmtKind.FUNCTION_DEF
    name: str
    type_params: list[AstTypeParam] = Field(default_factory=list)
    body: list[AstStmt] = Field(default_factory=list)
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
    type_comment: str | None = None
    arguments: list[AstAssign | AstAnnAssign] = Field(default_factory=list)

    @property
    def is_overload(self) -> bool:
        return any(
            (
                isinstance(decorator, AstName) and decorator.id == "overload"
                for decorator in self.decorator_list
            )
        )

    @property
    def is_getter_property(self) -> bool:
        return any(
            (
                isinstance(decorator, AstName)
                and decorator.id in ["property", "hybird_property"]
                for decorator in self.decorator_list
            )
        )

    @property
    def is_setter_property(self) -> bool:
        for decorator in self.decorator_list:
            if not isinstance(decorator, AstAttribute):
                continue
            if decorator.attr == "setter":
                return True
        return False

    @property
    def is_deleter_property(self) -> bool:
        for decorator in self.decorator_list:
            if not isinstance(decorator, AstAttribute):
                continue
            if decorator.attr == "deleter":
                return True
        return False

    @property
    def is_expression_property(self) -> bool:
        for decorator in self.decorator_list:
            if not isinstance(decorator, AstAttribute):
                continue
            if decorator.attr == "expression":
                return True
        return False
