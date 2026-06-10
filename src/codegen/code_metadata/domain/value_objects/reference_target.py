from typing import Self
from pydantic import Field
from pydantic import model_validator
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.shared.domain.core.entity import Entity
from codegen.shared.domain.enums import PythonBuiltinType


class ReferenceTarget(Entity):
    module_id: ModuleId | None = Field(default=None)
    component_id: ComponentId | None = Field(default=None)
    attribute_id: AttributeId | None = Field(default=None)
    builtin_type: PythonBuiltinType | None = Field(default=None)
    context: str | None = Field(default=None)
    raw: str | None = Field(default=None)

    @property
    def is_resolved(self) -> bool:
        if self.module_id:
            return True
        if self.component_id:
            return True
        if self.attribute_id:
            return True
        if self.builtin_type:
            return True
        if self.context:
            return True
        return False

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if self.module_id is not None:
            return self
        if self.component_id is not None:
            return self
        if self.attribute_id is not None:
            return self
        if self.builtin_type is not None:
            return self
        if self.context is not None:
            return self
        if self.raw is not None:
            return self
        raise ValueError(
            "target must be a ComponentId, AttributeId, or PythonBuiltinType"
        )

    def resolve(self, map: dict[str, Self]) -> Self:
        if self.is_resolved:
            return self
        if self.raw in PythonBuiltinType._value2member_map_:
            self.builtin_type = PythonBuiltinType(self.raw)
            self.raw = None
            return self
        if self.raw not in map:
            return self
        reference = map[self.raw]
        if reference.module_id:
            self.module_id = reference.module_id
        if reference.component_id:
            self.component_id = reference.component_id
        if reference.attribute_id:
            self.attribute_id = reference.attribute_id
        return self
