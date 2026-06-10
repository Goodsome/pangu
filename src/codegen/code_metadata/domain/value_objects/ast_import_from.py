from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_alias import AstAlias


class AstImportFrom(ValueObject):
    kind: Literal[AstStmtKind.IMPORT_FROM] = AstStmtKind.IMPORT_FROM
    module: str | None = None
    names: list[AstAlias]
    level: int = 0
