import re
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import ClassVar
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.value_objects.parsed_path import ParsedPath


@dataclass
class PathParser:
    dir_to_type_registry: dict[ComponentDir, ComponentType]
    PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        "codegen\\.(?P<context>[^.]+)\\.(?P<layer>[^.]+)\\.(?P<dir>[^.]+)"
    )

    @staticmethod
    def normalize(path: Path) -> str:
        p = PurePosixPath(path)
        parts = list(p.parts)
        if p.suffix:
            parts[-1] = p.stem
        normalized = ".".join(parts)
        if normalized.endswith(".__init__"):
            normalized = normalized[: -len(".__init__")]
        return normalized

    def parse_file_path(self, path: Path) -> ParsedPath:
        module_path = self.normalize(path)
        return self.parse_module_path(module_path)

    def parse_module_path(self, module_path: str) -> ParsedPath:
        match = self.PATTERN.search(module_path)
        if not match:
            return ParsedPath(
                context=module_path,
                layer=ArchitectureLayer.UNKNOWN,
                component_type=ComponentType.EXTERNAL,
            )
        groups = match.groupdict()
        context = groups["context"]
        dir_str = groups["dir"]
        layer = groups["layer"]
        component_dir = ComponentDir(dir_str)
        component_type = self.dir_to_type_registry[component_dir]
        return ParsedPath(
            context=context,
            layer=ArchitectureLayer(layer),
            component_type=component_type,
        )
