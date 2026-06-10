from typing import Any
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.instance_id import InstanceId
from codegen.shared.domain.core.entity import Entity


class Instance(Entity):
    id: InstanceId
    component_id: ComponentId
    name: str
    payload: dict[str, Any]
