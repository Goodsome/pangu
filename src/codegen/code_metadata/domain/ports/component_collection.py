from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId


class ComponentCollection(ABC):

    @abstractmethod
    def get_or_create_component(
        self,
        context: str,
        name: str,
        component_kind: ComponentKind = ComponentKind.CLASS,
    ) -> Component: ...

    @abstractmethod
    def get_or_create_attribute(
        self, component_id: ComponentId, name: str
    ) -> Attribute: ...
