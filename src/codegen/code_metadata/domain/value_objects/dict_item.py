from __future__ import annotations
from typing import TYPE_CHECKING
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.identifiers.component_id import ComponentId

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.expr_def import ExprDef


class DictItem(ValueObject):
    key: ExprDef | None
    value: ExprDef

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.key is not None:
            result.update(self.key.get_component_ids())
        result.update(self.value.get_component_ids())
        return result
