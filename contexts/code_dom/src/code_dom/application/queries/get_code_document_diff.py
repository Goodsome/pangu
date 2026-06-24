from dataclasses import dataclass
from pydantic import BaseModel
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.ports.code_generator import CodeGenerator
from code_dom.domain.ports.code_similarity_calculator import CodeSimilarityCalculator
from code_dom.application.dtos.file_metrics import FileMetrics
from foundation.system.file_system_port import FileSystemPort


class GetCodeDocumentDiffQuery(BaseModel):
    code_document: CodeDocument


@dataclass
class GetCodeDocumentDiffHandler:
    code_generator: CodeGenerator
    file_system: FileSystemPort
    code_similarity_calculator: CodeSimilarityCalculator

    def execute(self, query: GetCodeDocumentDiffQuery) -> FileMetrics:
        code_document = query.code_document
        generate_code = self.code_generator.generate(code_document)
        if not self.file_system.exists(code_document.physical_path):
            current_code = ""
        else:
            current_code = self.file_system.read_file(code_document.physical_path)
        similarity = self.code_similarity_calculator.calculate_similarity(
            current_code, generate_code
        )
        return FileMetrics(
            file_name=code_document.physical_path.stem,
            component_type="",
            ast_similarity=similarity,
            original_code=current_code,
            generated_code=generate_code,
            original_lines=len(current_code.splitlines()),
            generated_lines=len(generate_code.splitlines()),
        )
