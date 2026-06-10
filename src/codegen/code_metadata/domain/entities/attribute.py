from typing import Self
from pydantic import Field
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.entity import Entity


class Attribute(Entity):
    id: AttributeId
    name: str
    type: TypeDef | None
    value: ExprDef | None = None
    value_v2: AstExpr | None = None
    description: str = Field(default="")

    @classmethod
    def create(cls, sync_data: AttributeSyncData) -> Self:
        return cls(
            id=AttributeId.create(),
            name=sync_data.name,
            type=sync_data.type,
            value=sync_data.value,
        )

    def update(self, sync_data: AttributeSyncData) -> None:
        self.name = sync_data.name
        self.type = sync_data.type
        self.value = sync_data.value

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.type:
            result.update(self.type.get_component_ids())
        if self.value:
            result.update(self.value.get_component_ids())
        return result
