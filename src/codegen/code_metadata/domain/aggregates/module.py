from __future__ import annotations
from collections.abc import Iterator
from typing import Annotated
from typing import Literal
from typing import Self
from typing import override
from pydantic import Field
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.value_objects.module_dependency import (
    ModuleDependency,
)
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class BaseModule(AggregateRoot[ModuleId]):
    name: str
    path: str

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield from []

    def collect_raw_reference_targets(self) -> Iterator[ReferenceTarget]:
        for reference_target in self.iter_reference_targets():
            if reference_target.is_resolved:
                continue
            yield reference_target

    def resolve(self, map: dict[str, ReferenceTarget]) -> Self:
        for reference_target in self.iter_reference_targets():
            reference_target.resolve(map)
        return self

    def get_dependency_modules(self) -> set[ModuleId]:
        return set()

    def get_dependency_components(self) -> set[ComponentId]:
        return set()
