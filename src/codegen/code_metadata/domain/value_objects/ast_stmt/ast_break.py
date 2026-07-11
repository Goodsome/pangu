from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstBreak(AstStmtBase):
    kind: Literal[AstStmtKind.BREAK] = AstStmtKind.BREAK
