from typing import Self
from pydantic import BaseModel
from pydantic import Field
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.shared.domain.value_objects.snake_string import SnakeString


class DevProgress(BaseModel):
    records: list[FileMetrics] = Field(default_factory=list)

    def add_record(self, record: FileMetrics):
        self.records.append(record)

    def filter_by_type(self, component_type: str) -> Self:
        self.records = [
            record for record in self.records if record.component_type == component_type
        ]
        return self

    def filter_by_name(self, component_name: str) -> Self:
        self.records = [
            record
            for record in self.records
            if record.file_name == SnakeString(component_name)
        ]
        return self

    @property
    def ast_progress(self) -> float:
        if not self.records:
            return 0.0
        return sum((record.ast_similarity for record in self.records)) / len(
            self.records
        )

    def order_by_type(self) -> Self:
        self.records.sort(key=lambda r: r.component_type)
        return self

    def get_record_by_name(self, component_name: str) -> FileMetrics | None:
        return next(
            (
                record
                for record in self.records
                if record.file_name == SnakeString(component_name)
            ),
            None,
        )
