from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_alias import AstAlias


class AstImport(AstStmtBase):
    kind: Literal[AstStmtKind.IMPORT] = AstStmtKind.IMPORT
    names: list[AstAlias]
