from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId


@dataclass
class ComponentRegistry:
    initial_components: list[Component]
    _store_by_id: dict[ComponentId, Component] = field(init=False)
    _store_by_name: dict[str, Component] = field(init=False)

    def __post_init__(self):
        self._store_by_id = {}
        self._store_by_name = {}
        for component in self.initial_components:
            self._store_by_id[component.id] = component
            self._store_by_name[component.name] = component

    def find_by_name(self, name: str) -> Component | None:
        return self._store_by_name.get(name)

    def find_by_id(self, id: ComponentId) -> Component | None:
        return self._store_by_id.get(id)

    def register(self, component: Component):
        self._store_by_id[component.id] = component
        self._store_by_name[component.name] = component
