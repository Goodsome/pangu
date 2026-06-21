from typing import ClassVar

from codegen.shared.domain.core.event import IntegrationEvent


class ModuleMovedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "architecture"
    old_path: str
    new_path: str
    affected_callers: list[str]
    old_module_fqn: str
    new_module_fqn: str
