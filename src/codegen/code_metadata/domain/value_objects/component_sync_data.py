from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.behavior_sync_data import (
    BehaviorSyncData,
)
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.value_object import ValueObject


class ComponentSyncData(ValueObject):
    context: str
    name: str
    kind: ComponentKind = ComponentKind.CLASS
    type: ComponentType
    description: str
    layer: ArchitectureLayer
    bases: list[TypeDef]
    attributes: list[AttributeSyncData]
    behaviors: list[BehaviorSyncData]
    members: list[ComponentId]
    discriminator: str | None
