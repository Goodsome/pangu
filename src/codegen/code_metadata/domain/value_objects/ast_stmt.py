from __future__ import annotations
from typing import Annotated
from pydantic import Field
from pydantic import TypeAdapter
from codegen.code_metadata.domain.value_objects.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_assert import AstAssert
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_for import AstFor
from codegen.code_metadata.domain.value_objects.ast_while import AstWhile
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_with import AstWith
from codegen.code_metadata.domain.value_objects.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_break import AstBreak
from codegen.code_metadata.domain.value_objects.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_try import AstTry
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef

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
    | AstClassDef,
    Field(discriminator="kind"),
]
ast_stmt_adapter: TypeAdapter[AstStmt] = TypeAdapter(AstStmt)
