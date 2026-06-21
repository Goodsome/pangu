from typing import ClassVar

from codegen.shared.domain.core.event import IntegrationEvent


class ModuleDeletedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "architecture"
    module_fqn: str
    is_package: bool
