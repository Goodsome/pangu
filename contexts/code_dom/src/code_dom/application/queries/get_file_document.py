from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.ports.code_parser import CodeParser


class GetFileDocumentQuery(BaseModel):
    file_path: Path


class GetFileDocumentResult(BaseModel):
    code_document: CodeDocument


@dataclass
class GetFileDocumentHandler:
    code_parser: CodeParser

    def handle(self, query: GetFileDocumentQuery) -> GetFileDocumentResult:
        code_document = self.code_parser.parse_file(query.file_path)
        return GetFileDocumentResult(code_document=code_document)
