from __future__ import annotations
from typing import Annotated
from pydantic import Field, TypeAdapter

from codegen.code_metadata.domain.value_objects.ast_stmt.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assert import AstAssert
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_break import AstBreak
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_for import AstFor
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_while import AstWhile
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_with import AstWith
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_try import AstTry
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_delete import AstDelete

from codegen.code_metadata.domain.value_objects.ast_except_handler import AstExceptHandler
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase

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

