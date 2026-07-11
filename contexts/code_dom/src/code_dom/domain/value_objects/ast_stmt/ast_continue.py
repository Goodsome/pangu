from typing import Literal
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstContinue(AstStmtBase):
    kind: Literal[AstStmtKind.CONTINUE] = AstStmtKind.CONTINUE
