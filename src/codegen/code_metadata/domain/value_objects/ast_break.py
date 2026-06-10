from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core.value_object import ValueObject


class AstBreak(ValueObject):
    kind: Literal[AstStmtKind.BREAK] = AstStmtKind.BREAK
