from dataclasses import dataclass
from pydantic import BaseModel
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_formatter import CodeFormatter
from codegen.code_dom.domain.ports.code_generator import CodeGenerator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class GenerateCodeCommand(BaseModel):
    code_documents: list[CodeDocument]


@dataclass
class GenerateCodeHandler:
    code_generator: CodeGenerator
    code_formatter: CodeFormatter
    file_system: FileSystemPort

    def execute(self, cmd: GenerateCodeCommand):
        for code_document in cmd.code_documents:
            code = self.code_generator.generate(code_document)
            code = self.code_formatter.format_code(code)
            self.file_system.write_file(
                path=code_document.physical_path, content=code, overwrite=True
            )
