from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.exceptions.attribute_not_found import (
    AttributeNotFound,
)
from codegen.code_metadata.domain.exceptions.dep_component_not_found import (
    DepComponentNotFound,
)
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.registries.module_registry import ModuleRegistry
from codegen.code_metadata.domain.registries.component_registry import ComponentRegistry
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget


@dataclass
class TranslateReference:
    id_map: dict[ComponentId, Component]
    attribute_id_map: dict[AttributeId, Attribute] = field(init=False)
    module_registry: ModuleRegistry
    component_registry: ComponentRegistry

    def __post_init__(self):
        self.attribute_id_map = {}
        for component in self.id_map.values():
            if not isinstance(component, ClassComponent):
                continue
            for attribute in component.attributes:
                self.attribute_id_map[attribute.id] = attribute

    def resolve_reference_target(self, target: ReferenceTarget) -> str:
        if target.component_id:
            return self.resolve_component_id(target.component_id)
        elif target.attribute_id:
            return self.resolve_attribute_id(target.attribute_id)
        elif target.builtin_type:
            return target.builtin_type
        elif target.context:
            return target.context
        elif target.raw:
            return target.raw
        raise ValueError(f"Unsupported target={target!r}")

    def resolve_component_id(self, component_id: ComponentId) -> str:
        if component_id not in self.id_map:
            raise DepComponentNotFound(component_id=component_id)
        return self.id_map[component_id].name

    def resolve_attribute_id(self, attribute_id: AttributeId) -> str:
        attribute = self.get_attribute(attribute_id)
        return attribute.name

    def get_attribute(self, attribute_id: AttributeId) -> Attribute:
        if attribute_id not in self.attribute_id_map:
            raise AttributeNotFound(attribute_id=attribute_id)
        return self.attribute_id_map[attribute_id]

    def get_component(self, component_id: ComponentId) -> Component:
        if component_id not in self.id_map:
            raise DepComponentNotFound(component_id=component_id)
        return self.id_map[component_id]

    def resolve_reference(self, reference: ReferenceTarget) -> str:
        if reference.module_id:
            module = self.module_registry.find_by_id(reference.module_id)
            if module is None:
                return reference.raw or ""
            return module.path
        elif reference.component_id:
            component = self.component_registry.find_by_id(reference.component_id)
            if component is None:
                return reference.raw or ""
            return component.name
        return reference.raw or ""
