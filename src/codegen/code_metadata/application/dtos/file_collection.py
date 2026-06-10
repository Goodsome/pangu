from pathlib import Path
from pydantic import BaseModel
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.value_objects.reference_source import ReferenceSource
from codegen.shared.domain.value_objects.pascal_string import PascalString


class FileCollection(BaseModel):
    context: str
    type: ComponentType
    layer: ArchitectureLayer
    code: str
    name: PascalString
    path: Path
    parsed_component: ParsedComponent
    reference_sources: list[ReferenceSource]

    def collect_dependency_components(self) -> set[tuple[str, str]]:
        result: set[tuple[str, str]] = set()
        for rs in self.reference_sources:
            for component in rs.components:
                result.add((rs.context, component))
        return result

    def collect_dependency_contexts_only(self) -> set[str]:
        result: set[str] = set()
        for rs in self.reference_sources:
            if not rs.components:
                result.add(rs.context)
        return result
