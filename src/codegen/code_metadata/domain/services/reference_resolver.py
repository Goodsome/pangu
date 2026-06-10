from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_collection import ComponentCollection
from codegen.code_metadata.domain.value_objects.reference_source import ReferenceSource
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class ReferenceResolver:
    component: Component
    components: ComponentCollection
    reference_sources: list[ReferenceSource]
    dep_contexts: set[str] = field(init=False)
    dep_components: set[str] = field(init=False)
    component_context_map: dict[str, str] = field(init=False)

    def __post_init__(self):
        self.dep_contexts = set()
        self.dep_components = set()
        self.component_context_map = {}
        for rs in self.reference_sources:
            self.dep_contexts.add(rs.context)
            for component in rs.components:
                self.dep_components.add(component)
                self.component_context_map[component] = rs.context

    def resolve_target(
        self, target: str, source_target: ReferenceTarget | None = None
    ) -> ReferenceTarget:
        if "." in target:
            first, remainder = target.split(".", 1)
            first_rt = self.resolve_target(first)
            return self.resolve_target(remainder, source_target=first_rt)
        if target in self.dep_contexts:
            return ReferenceTarget(context=target)
        if target in PythonBuiltinType._value2member_map_:
            return ReferenceTarget(builtin_type=PythonBuiltinType(target))
        if target in self.dep_components:
            return self.resolve_target_to_component_id(target=target)
        if target == self.component.name:
            return ReferenceTarget(component_id=self.component.id)
        if source_target is None:
            print(f"Resolving target target={target!r} without source target")
            return ReferenceTarget(raw=target)
        if source_target.context:
            return self.resolve_target_to_component_id(
                target=target, context=source_target.context
            )
        if source_target.component_id:
            return self.resolve_target_to_attribute_id(
                target=target, component_id=source_target.component_id
            )
        raise NotImplementedError(
            f"target={target!r}, source_target={source_target!r}, self.component={self.component!r}"
        )

    def resolve_target_to_component_id(
        self, target: str, context: str | None = None
    ) -> ReferenceTarget:
        if context is None:
            context = self.component_context_map[target]
        component = self.components.get_or_create_component(
            context=context, name=target
        )
        return ReferenceTarget(component_id=component.id)

    def resolve_target_to_attribute_id(
        self, target: str, component_id: ComponentId
    ) -> ReferenceTarget:
        attribute = self.components.get_or_create_attribute(component_id, target)
        return ReferenceTarget(attribute_id=attribute.id)

    def get_component_id(self, name: str) -> ComponentId:
        context = self.component_context_map[name]
        component = self.components.get_or_create_component(context=context, name=name)
        return component.id
