from typing import ClassVar
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy


class PolicyPolicy(ComponentPolicy):
    component_type: ClassVar[ComponentType] = ComponentType.POLICY
    dir_name: ClassVar[ComponentDir] = ComponentDir.POLICIES
