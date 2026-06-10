from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr


class DictItemDto(BaseModel):
    key: ParsedExpr | None
    value: ParsedExpr
