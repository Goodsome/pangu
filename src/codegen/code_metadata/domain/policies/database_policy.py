from typing import ClassVar
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class DatabasePolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.DATABASE
    dir_name: ClassVar[ComponentDir] = ComponentDir.DATABASE
