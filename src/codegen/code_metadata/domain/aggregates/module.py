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


class FileModule(BaseModule):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE
    components: list[Component]
    dependencies: list[ModuleDependency]
    dir_module_id: ModuleId | None

    def find_component(self, name: str) -> Component | None:
        for component in self.components:
            if component.name == name:
                return component
        return None

    def find_components_by_ids(self, ids: set[ComponentId]) -> list[Component]:
        return [component for component in self.components if component.id in ids]

    @override
    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        for component in self.components:
            yield from component.iter_reference_targets()
        for dependency in self.dependencies:
            yield from dependency.iter_reference_targets()

    def bind_dir_module_id(self, dir_module_id: ModuleId) -> None:
        self.dir_module_id = dir_module_id

    @override
    def get_dependency_modules(self) -> set[ModuleId]:
        result: set[ModuleId] = set()
        for dependency in self.dependencies:
            if dependency.module.module_id:
                result.add(dependency.module.module_id)
        return result

    @override
    def get_dependency_components(self) -> set[ComponentId]:
        depdendency_components: set[ComponentId] = set()
        for dependency in self.dependencies:
            if dependency.component is None:
                continue
            if dependency.component.component_id is None:
                continue
            depdendency_components.add(dependency.component.component_id)
        return depdendency_components


class DirectoryModule(BaseModule):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY
    public_component_ids: list[ReferenceTarget]
    sub_module_ids: list[ModuleId]
    dir_module_id: ModuleId | None

    @override
    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield from self.public_component_ids

    def bind_sub_module_id(self, sub_module_id: ModuleId) -> None:
        if sub_module_id in self.sub_module_ids:
            return
        self.sub_module_ids.append(sub_module_id)

    def bind_dir_module_id(self, dir_module_id: ModuleId) -> None:
        self.dir_module_id = dir_module_id

    @override
    def get_dependency_components(self) -> set[ComponentId]:
        dependency_component_ids: set[ComponentId] = set()
        for rt in self.public_component_ids:
            if rt.component_id is None:
                continue
            dependency_component_ids.add(rt.component_id)
        return dependency_component_ids


class ExternalModule(BaseModule):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    components: list[Component]

    def find_component(self, name: str) -> Component | None:
        for component in self.components:
            if component.name == name:
                return component
        return None


Module = Annotated[
    FileModule | DirectoryModule | ExternalModule, Field(discriminator="kind")
]
