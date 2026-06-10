from pathlib import Path
from pydantic import BaseModel
from pydantic import Field


class PathScanCriteria(BaseModel):
    base_dir: Path
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)
