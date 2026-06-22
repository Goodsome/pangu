from pathlib import Path
from typing import ClassVar
from foundation.building_blocks.event import IntegrationEvent


class ModuleCreatedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "architecture"
    module_fqn: str
    module_path: Path
    is_package: bool
