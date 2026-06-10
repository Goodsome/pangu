from pydantic import BaseModel
from pydantic import Field
from typing import Literal
from typing import Annotated
from pathlib import Path
from codegen.code_metadata.domain.enums.module_kind import ModuleKind


class BaseScanResult(BaseModel):
    path: Path
    name: str


class FileScanResult(BaseScanResult):
    kind: Literal[ModuleKind.FILE] = ModuleKind.FILE
    extension: str


ScanResult = Annotated[FileScanResult, Field(discriminator="kind")]
