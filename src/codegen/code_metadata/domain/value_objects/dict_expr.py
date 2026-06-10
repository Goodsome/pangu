from pydantic import Field
from typing_extensions import Literal
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.value_objects.dict_item import DictItem
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.identifiers.component_id import ComponentId


class DictExpr(ValueObject):
    kind: Literal[ExprKind.DICT] = ExprKind.DICT
    items: list[DictItem] = Field(default_factory=list)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        for item in self.items:
            result.update(item.get_component_ids())
        return result
