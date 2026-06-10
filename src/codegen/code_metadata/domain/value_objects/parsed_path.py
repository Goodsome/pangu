from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.shared.domain.core.value_object import ValueObject


class ParsedPath(ValueObject):
    context: str
    layer: ArchitectureLayer
    component_type: ComponentType
