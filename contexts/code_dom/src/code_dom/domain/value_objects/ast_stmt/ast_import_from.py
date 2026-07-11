from __future__ import annotations
from typing import Literal
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from code_dom.domain.value_objects.ast_stmt.ast_alias import AstAlias


class AstImportFrom(AstStmtBase):
    kind: Literal[AstStmtKind.IMPORT_FROM] = AstStmtKind.IMPORT_FROM
    module: str | None = None
    names: list[AstAlias]
    level: int = 0
