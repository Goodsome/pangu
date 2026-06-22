from pathlib import Path
from typing import ClassVar

from codegen.shared.domain.core.event import IntegrationEvent


class ModuleCreatedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "architecture"
    module_fqn: str
    module_path: Path
    is_package: bool
    