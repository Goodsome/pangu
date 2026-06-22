from pathlib import Path
from typing import ClassVar
from foundation.building_blocks.event import IntegrationEvent


class ModuleMovedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "architecture"
    old_path: Path
    new_path: Path
    affected_callers: list[Path]
    old_module_fqn: str
    new_module_fqn: str
