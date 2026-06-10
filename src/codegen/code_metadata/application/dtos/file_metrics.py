from pydantic import BaseModel


class FileMetrics(BaseModel):
    file_name: str
    component_type: str
    ast_similarity: float
    original_lines: int
    generated_lines: int
    original_code: str
    generated_code: str

    @property
    def line_diff(self) -> int:
        return self.generated_lines - self.original_lines
