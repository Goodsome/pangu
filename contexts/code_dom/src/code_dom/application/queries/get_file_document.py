from dataclasses import dataclass
from pathlib import Path

from foundation.system.file_system_port import FileSystemPort
from pydantic import BaseModel

from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.ports.code_parser import CodeParser


class GetFileDocumentQuery(BaseModel):
    file_path: Path


class GetFileDocumentResult(BaseModel):
    code_document: CodeDocument
    file_exists: bool


@dataclass
class GetFileDocumentHandler:
    code_parser: CodeParser
    file_system: FileSystemPort

    def execute(self, query: GetFileDocumentQuery) -> GetFileDocumentResult:
        file_exists = self.file_system.exists(query.file_path)
        if not file_exists:
            return GetFileDocumentResult(
                code_document=CodeDocument(
                    id=query.file_path,
                    physical_path=query.file_path,
                    body=[],
                    description=None,
                ),
                file_exists=False,
            )
        code_document = self.code_parser.parse_file(query.file_path)
        return GetFileDocumentResult(
            code_document=code_document,
            file_exists=True,
        )
