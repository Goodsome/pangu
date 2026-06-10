from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_parser import CodeParser


class GetProjectDocumentsQuery(BaseModel):
    dir_path: Path


class GetProjectDocumentsResult(BaseModel):
    code_documents: list[CodeDocument]


@dataclass
class GetProjectDocumentsHandler:
    code_parser: CodeParser

    def handle(self, query: GetProjectDocumentsQuery) -> GetProjectDocumentsResult:
        path = query.dir_path
        file_path = query.dir_path.with_suffix(".py")
        if path.is_dir():
            code_documents = self.code_parser.parse_directory(query.dir_path)
        elif file_path.is_file():
            code_document = self.code_parser.parse_file(file_path)
            code_documents = [code_document]
        else:
            raise ValueError(f"not exist path={path!r}")
        return GetProjectDocumentsResult(code_documents=code_documents)
