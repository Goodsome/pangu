from __future__ import annotations
from collections.abc import Iterator
from typing import Annotated
from typing import Literal
from typing import Self
from pydantic import Field
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.behavior_sync_data import (
    BehaviorSyncData,
)
from codegen.code_metadata.domain.value_objects.component_sync_data import (
    ComponentSyncData,
)
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.aggregate_root import AggregateRoot
from codegen.shared.domain.value_objects.snake_string import SnakeString


class BaseComponent(AggregateRoot[ComponentId]):
    module_id: ModuleId
    name: str
    context: str
    layer: ArchitectureLayer
    type: ComponentType


class UnionComponent(BaseComponent):
    """union component"""

    kind: Literal[ComponentKind.UNION] = ComponentKind.UNION
    description: str
    discriminator: str | None = None
    members: list[ReferenceTarget] = Field(default_factory=list)

    @property
    def file_name(self) -> str:
        return SnakeString(self.name)

    def get_dependencies(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        return result

    def update(self, component_sync_data: ComponentSyncData) -> None:
        self.type = component_sync_data.type
        self.name = component_sync_data.name
        self.context = component_sync_data.context
        self.layer = component_sync_data.layer
        self.discriminator = component_sync_data.discriminator

    def get_import_module(self, type_policy: ComponentPolicy) -> str:
        if self.type is ComponentType.EXTERNAL:
            return self.context
        dir_name = type_policy.dir_name
        return (
            f"codegen.{self.context}.{self.layer}.{dir_name}.{SnakeString(self.name)}"
        )

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield from self.members


class ClassComponent(BaseComponent):
    """class component"""

    kind: Literal[ComponentKind.CLASS] = ComponentKind.CLASS
    description: str
    bases: list[TypeDef] = Field(default_factory=list)
    attributes: list[Attribute] = Field(default_factory=list)
    behaviors: list[Behavior] = Field(default_factory=list)

    @property
    def file_name(self) -> str:
        return SnakeString(self.name)

    def get_dependencies(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        for base in self.bases:
            result.update(base.get_component_ids())
        for attr in self.attributes:
            result.update(attr.get_component_ids())
        for behavior in self.behaviors:
            result.update(behavior.get_component_ids())
        return result

    def update(self, component_sync_data: ComponentSyncData) -> None:
        self.type = component_sync_data.type
        self.name = component_sync_data.name
        self.description = component_sync_data.description
        self.context = component_sync_data.context
        self.layer = component_sync_data.layer
        self.bases = component_sync_data.bases
        self.sync_attributes(component_sync_data.attributes)
        self.sync_behaviors(component_sync_data.behaviors)

    def sync_attributes(self, attributes: list[AttributeSyncData]) -> None:
        existing_attributes = {attr.name: attr for attr in self.attributes}
        synced_attrs: list[Attribute] = []
        for attr_sync_data in attributes:
            if attr_sync_data.name in existing_attributes:
                attr = existing_attributes[attr_sync_data.name]
                attr.update(attr_sync_data)
            else:
                attr = Attribute.create(attr_sync_data)
            synced_attrs.append(attr)
        self.attributes = synced_attrs

    def sync_behaviors(self, behaviors: list[BehaviorSyncData]) -> None:
        existing_behaviors = {b.name: b for b in self.behaviors}
        synced_behaviors: list[Behavior] = []
        for sync_data in behaviors:
            if sync_data.name in existing_behaviors:
                behavior = existing_behaviors[sync_data.name]
                behavior.update(sync_data)
            else:
                behavior = Behavior.create(sync_data)
            synced_behaviors.append(behavior)
        self.behaviors = synced_behaviors

    def add_attribute(self, name: str) -> Attribute:
        attr = Attribute(id=AttributeId.create(), name=name, type=None, value_v2=None)
        self.attributes.append(attr)
        return attr

    def find_attribute(self, name: str) -> Attribute | None:
        return next((attr for attr in self.attributes if attr.name == name), None)

    def find_attribute_by_id(self, attribute_id: AttributeId) -> Attribute | None:
        return next((attr for attr in self.attributes if attr.id == attribute_id), None)

    def get_import_module(self, type_policy: ComponentPolicy) -> str:
        if self.type is ComponentType.EXTERNAL:
            return self.context
        dir_name = type_policy.dir_name
        return (
            f"codegen.{self.context}.{self.layer}.{dir_name}.{SnakeString(self.name)}"
        )

    def find_behavior(self, name: str) -> Behavior | None:
        return next((b for b in self.behaviors if b.name == name), None)

    def resolve(self, map: dict[str, ReferenceTarget]) -> Self:
        for base in self.bases:
            base.resolve(map)
        return self

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        for base in self.bases:
            yield from base.iter_reference_targets()


Component = Annotated[ClassComponent | UnionComponent, Field(discriminator="kind")]
