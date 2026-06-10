from pathlib import Path
from typing import Annotated
from typing import Literal
from pydantic import BaseModel
from pydantic import Field
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.domain.enums.module_kind import ModuleKind


class ParsedFileModule(BaseModel):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE
    name: str
    path: Path
    components: list[ParsedComponent]
    dependencies: list[ImportDto]

    @property
    def import_path(self) -> str:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.with_suffix("").parts
        return ".".join(parts)

    def dependency_modules(self) -> set[str]:
        result: set[str] = set()
        for dependency in self.dependencies:
            module_path = dependency.resolve_module_path(self.path)
            result.add(module_path)
        return result

    def father_paths(self) -> set[str]:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.with_suffix("").parts
        result: set[str] = set()
        for i in range(1, len(parts)):
            result.add(".".join(parts[:i]))
        return result


class ParsedDirectoryModule(BaseModel):
    kind: Literal[ModuleKind.DIRECTORY] = ModuleKind.DIRECTORY
    name: str
    path: Path
    public_component_names: list[str]

    @property
    def import_path(self) -> str:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.parts
        return ".".join(parts)

    def dependency_modules(self) -> set[str]:
        return set()

    def father_paths(self) -> set[str]:
        root_path = Path("src")
        relative_path = self.path.relative_to(root_path)
        parts = relative_path.parts
        result: set[str] = set()
        for i in range(1, len(parts)):
            result.add(".".join(parts[:i]))
        return result


class ParsedExternalModule(BaseModel):
    kind: Literal[ModuleKind.EXTERNAL] = ModuleKind.EXTERNAL
    name: str
    components: list[str]

    @property
    def import_path(self) -> str:
        return self.name

    def dependency_modules(self) -> set[str]:
        return set()

    def father_paths(self) -> set[str]:
        return set()


ParsedModule = Annotated[
    ParsedFileModule | ParsedDirectoryModule | ParsedExternalModule,
    Field(discriminator="kind"),
]
