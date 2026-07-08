from pathlib import Path
from typing import ClassVar
from foundation.building_blocks.event import IntegrationEvent


class ClassMovedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "code_structure"
    class_name: str
    current_module_path: Path
    target_module_path: Path
    current_module_fqn: str
    target_module_fqn: str
    affected_callers: list[Path]
