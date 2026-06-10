from abc import ABC
from typing import ClassVar
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir


class ComponentPolicy(ABC):
    component_type: ClassVar[ComponentType]
    dir_name: ClassVar[ComponentDir]
