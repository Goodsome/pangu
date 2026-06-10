from typing import override
from pydantic import BaseModel


class ImportedComponent(BaseModel):
    context: str
    name: str
    import_module: str

    @override
    def __hash__(self) -> int:
        return hash((self.import_module, self.name))
