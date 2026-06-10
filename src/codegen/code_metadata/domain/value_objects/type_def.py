from collections.abc import Iterator
from typing import Self
from pydantic import Field
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.value_object import ValueObject


class TypeDef(ValueObject):
    origin: ReferenceTarget
    args: tuple[Self, ...] = Field(default_factory=tuple)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.origin.component_id:
            result.add(self.origin.component_id)
        for arg in self.args:
            result.update(arg.get_component_ids())
        return result

    def resolve(self, map: dict[str, ReferenceTarget]) -> Self:
        self.origin.resolve(map)
        for arg in self.args:
            arg.resolve(map)
        return self

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield self.origin
        for arg in self.args:
            yield from arg.iter_reference_targets()
