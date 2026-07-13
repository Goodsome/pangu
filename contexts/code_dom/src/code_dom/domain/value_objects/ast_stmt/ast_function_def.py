from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_type_param import AstTypeParam
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_expr.ast_attribute import AstAttribute
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from code_dom.domain.value_objects.ast_stmt.ast_assign import AstAssign
from code_dom.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign


class AstFunctionDef(AstStmtBase):
    lineno: int
    kind: Literal[AstStmtKind.FUNCTION_DEF] = AstStmtKind.FUNCTION_DEF
    is_async: bool = False
    name: str
    type_params: list[AstTypeParam] = Field(default_factory=list)
    arguments: list[AstAssign | AstAnnAssign] = Field(default_factory=list)
    body: list[AstStmtBase] = Field(default_factory=list)
    decorator_list: list[AstExprBase] = Field(default_factory=list)
    returns: AstExprBase | None = None
    type_comment: str | None = None

    @property
    def is_overload(self) -> bool:
        return self.check_something_in_decorator_list("overload")

    @property
    def is_override(self) -> bool:
        return self.check_something_in_decorator_list("override")

    def check_something_in_decorator_list(self, something: str):
        return any(
            (
                isinstance(decorator, AstName) and decorator.id == something
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
