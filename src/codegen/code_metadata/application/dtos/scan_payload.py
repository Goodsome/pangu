from pydantic import BaseModel
from codegen.code_metadata.application.dtos.scan_result import ScanResult


class ScanPayload(BaseModel):
    result: list[ScanResult]
