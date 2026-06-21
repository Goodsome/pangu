from typing import ClassVar
from codegen.shared.domain.core.event import IntegrationEvent


class ModuleCreatedIntegrationEvent(IntegrationEvent):
    __domain_entity: ClassVar[str] = "architecture"
    module_fqn: str
    is_package: bool
    