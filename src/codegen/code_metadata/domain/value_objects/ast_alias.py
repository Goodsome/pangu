from __future__ import annotations
from codegen.shared.domain.core.value_object import ValueObject


class AstAlias(ValueObject):
    name: str
    asname: str | None = None
