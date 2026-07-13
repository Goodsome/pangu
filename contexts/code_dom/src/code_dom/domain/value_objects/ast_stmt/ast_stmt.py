from __future__ import annotations
from typing import Annotated
from pydantic import Field, TypeAdapter

from code_dom.domain.value_objects.ast_stmt.ast_return import AstReturn
from code_dom.domain.value_objects.ast_stmt.ast_raise import AstRaise
from code_dom.domain.value_objects.ast_stmt.ast_assert import AstAssert
from code_dom.domain.value_objects.ast_stmt.ast_pass import AstPass
from code_dom.domain.value_objects.ast_stmt.ast_break import AstBreak
from code_dom.domain.value_objects.ast_stmt.ast_continue import AstContinue
from code_dom.domain.value_objects.ast_stmt.ast_assign import AstAssign
from code_dom.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from code_dom.domain.value_objects.ast_stmt.ast_aug_assign import AstAugAssign
from code_dom.domain.value_objects.ast_stmt.ast_expr_stmt import AstExprStmt
from code_dom.domain.value_objects.ast_stmt.ast_for import AstFor
from code_dom.domain.value_objects.ast_stmt.ast_while import AstWhile
from code_dom.domain.value_objects.ast_stmt.ast_if import AstIf
from code_dom.domain.value_objects.ast_stmt.ast_with import AstWith
from code_dom.domain.value_objects.ast_stmt.ast_match import AstMatch
from code_dom.domain.value_objects.ast_stmt.ast_try import AstTry
from code_dom.domain.value_objects.ast_stmt.ast_function_def import AstFunctionDef
from code_dom.domain.value_objects.ast_stmt.ast_import import AstImport
from code_dom.domain.value_objects.ast_stmt.ast_import_from import AstImportFrom
from code_dom.domain.value_objects.ast_stmt.ast_class_def import AstClassDef
from code_dom.domain.value_objects.ast_stmt.ast_delete import AstDelete


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

# model_rebuild 已经不再需要，因为字段类型 (AstStmtBase) 在定义期均已完全解析，不再含有对联合类型 AstStmt 的循环 ForwardRef。
