from dataclasses import dataclass
from typing import overload
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.component import UnionComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.registries.component_registry import ComponentRegistry
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class SyncModuleContext:
    module_id: ModuleId
    module: ParsedFileModule
    component_registry: ComponentRegistry
    path_parser: PathParser

    def parsed_component_to_component(
        self, parsed_component: ParsedComponent
    ) -> Component:
        if parsed_component.is_union:
            component = self.parsed_component_to_union_component(parsed_component)
        else:
            component = self.parsed_component_to_class_component(parsed_component)
        self.component_registry.register(component)
        return component

    def parsed_component_to_class_component(
        self, parsed_component: ParsedComponent
    ) -> ClassComponent:
        component = self.component_registry.find_by_name(parsed_component.name)
        if isinstance(component, UnionComponent):
            raise ValueError(f"not support component={component!r}")
        if component is None:
            component_id = ComponentId.create()
        else:
            component_id = component.id
        parsed_path = self.path_parser.parse_file_path(self.module.path)
        bases = [
            self.parsed_type_to_type_def(parsed_type)
            for parsed_type in parsed_component.bases
        ]
        attributes = [
            self.parsed_attribute_to_attribute(a, component)
            for a in parsed_component.attributes
        ]
        behaviors = [
            self.parsed_behavior_to_behavior(b, component)
            for b in parsed_component.behaviors
        ]
        return ClassComponent(
            module_id=self.module_id,
            id=component_id,
            name=parsed_component.name,
            context=parsed_path.context,
            layer=parsed_path.layer,
            type=parsed_path.component_type,
            description=parsed_component.description,
            bases=bases,
            attributes=attributes,
            behaviors=behaviors,
        )

    def parsed_component_to_union_component(
        self, parsed_component: ParsedComponent
    ) -> UnionComponent:
        component = self.component_registry.find_by_name(parsed_component.name)
        if component is None:
            component_id = ComponentId.create()
        else:
            component_id = component.id
        parsed_path = self.path_parser.parse_file_path(self.module.path)
        members = [ReferenceTarget(raw=m) for m in parsed_component.members]
        return UnionComponent(
            id=component_id,
            module_id=self.module_id,
            name=parsed_component.name,
            context=parsed_path.context,
            layer=parsed_path.layer,
            type=parsed_path.component_type,
            description=parsed_component.description,
            discriminator=parsed_component.discriminator,
            members=members,
        )

    @overload
    def parsed_type_to_type_def(self, parsed_type: ParsedType) -> TypeDef: ...

    @overload
    def parsed_type_to_type_def(self, parsed_type: None) -> None: ...

    def parsed_type_to_type_def(self, parsed_type: ParsedType | None) -> TypeDef | None:
        if parsed_type is None:
            return None
        origin = self.resolve_target(parsed_type.origin)
        args = tuple((self.parsed_type_to_type_def(arg) for arg in parsed_type.args))
        return TypeDef(origin=origin, args=args)

    def resolve_target(self, target: str) -> ReferenceTarget:
        return ReferenceTarget(raw=target)

    def parsed_attribute_to_attribute(
        self, parsed_attribute: ParsedAttribute, component: ClassComponent | None
    ) -> Attribute:
        if component is not None:
            attribute = component.find_attribute(parsed_attribute.name)
        else:
            attribute = None
        if attribute is None:
            attribute_id = AttributeId.create()
        else:
            attribute_id = attribute.id
        type_def = self.parsed_type_to_type_def(parsed_attribute.type)
        return Attribute(
            id=attribute_id,
            name=parsed_attribute.name,
            type=type_def,
            value_v2=parsed_attribute.value_v2,
        )

    def parsed_behavior_to_behavior(
        self, parsed_behavior: ParsedBehavior, component: ClassComponent | None
    ) -> Behavior:
        if component is not None:
            behavior = component.find_behavior(parsed_behavior.name)
        else:
            behavior = None
        if behavior is None:
            behavior_id = BehaviorId.create()
        else:
            behavior_id = behavior.id
        inputs = [
            self.parsed_attribute_to_attribute(a, component)
            for a in parsed_behavior.inputs
        ]
        output = self.parsed_type_to_type_def(parsed_behavior.output)
        return Behavior(
            id=behavior_id,
            name=parsed_behavior.name,
            description=parsed_behavior.description or "",
            scenarios=[],
            inputs=inputs,
            output=output,
            body=parsed_behavior.body,
        )
