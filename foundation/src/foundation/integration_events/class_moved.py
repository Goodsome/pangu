from pathlib import Path
from typing import ClassVar, TypedDict
from foundation.building_blocks.event import IntegrationEvent


class ModuleDepDict(TypedDict):
    module: str
    symbol: str
    alias: str | None


class ClassMovedIntegrationEvent(IntegrationEvent):
    __domain_entity__: ClassVar[str] = "code_structure"
    class_name: str
    current_module_path: Path
    target_module_path: Path
    current_module_fqn: str
    target_module_fqn: str
    affected_callers: list[Path]
    current_module_deps: list[ModuleDepDict]
    target_module_deps: list[ModuleDepDict]
