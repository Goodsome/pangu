from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from foundation.building_blocks.value_object import ValueObject


class AstContinue(ValueObject):
    kind: Literal[AstStmtKind.CONTINUE] = AstStmtKind.CONTINUE
