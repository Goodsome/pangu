from pathlib import Path
from pydantic import BaseModel


class ParsedModule(BaseModel):
    file_path: Path
    raw_imports: list[str]