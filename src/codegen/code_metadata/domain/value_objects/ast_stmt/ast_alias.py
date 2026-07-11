from __future__ import annotations
from foundation.building_blocks.value_object import ValueObject


class AstAlias(ValueObject):
    name: str
    asname: str | None = None
