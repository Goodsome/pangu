from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assert import AstAssert
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_break import AstBreak
from codegen.code_metadata.domain.value_objects.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_delete import AstDelete
from codegen.code_metadata.domain.value_objects.ast_except_handler import AstExceptHandler
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)
from codegen.code_metadata.domain.value_objects.ast_try import AstTry
from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeParam
from codegen.code_metadata.domain.value_objects.ast_while import AstWhile
from codegen.code_metadata.domain.value_objects.ast_with import AstWith
from foundation.building_blocks.value_object import ValueObject
from pydantic import Field, TypeAdapter
from typing import Literal, Annotated


class AstFunctionDef(ValueObject):
    lineno: int
    kind: Literal[AstStmtKind.FUNCTION_DEF] = AstStmtKind.FUNCTION_DEF
    is_async: bool = False
    name: str
    type_params: list[AstTypeParam] = Field(default_factory=list)
    arguments: list[AstAssign | AstAnnAssign] = Field(default_factory=list)
    body: list[AstStmt] = Field(default_factory=list)
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
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


class AstFor(ValueObject):
    kind: Literal[AstStmtKind.FOR] = AstStmtKind.FOR
    target: AstExpr
    iter: AstExpr
    body: list[AstStmt] = Field(default_factory=list)
    orelse: list[AstStmt] = Field(default_factory=list)


AstStmt = Annotated[
    AstReturn
    | AstRaise
    | AstAssert
    | AstPass
    | AstBreak
    | AstContinue
    | AstAssign
    | AstAnnAssign
    | AstAugAssign
    | AstExprStmt
    | AstFor
    | AstWhile
    | AstIf
    | AstWith
    | AstMatch
    | AstTry
    | AstFunctionDef
    | AstImport
    | AstImportFrom
    | AstClassDef
    | AstDelete,
    Field(discriminator="kind"),
]
ast_stmt_adapter: TypeAdapter[AstStmt] = TypeAdapter(AstStmt)
AstFor.model_rebuild()
AstIf.model_rebuild()
AstWith.model_rebuild()
AstMatch.model_rebuild()
AstTry.model_rebuild()
AstFunctionDef.model_rebuild()
AstReturn.model_rebuild()
AstRaise.model_rebuild()
AstImport.model_rebuild()
AstImportFrom.model_rebuild()
AstClassDef.model_rebuild()
AstDelete.model_rebuild()
AstWhile.model_rebuild()
AstMatchCase.model_rebuild()
AstExceptHandler.model_rebuild()
