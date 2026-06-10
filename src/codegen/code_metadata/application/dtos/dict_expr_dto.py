from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Literal
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto


class DictExprDto(BaseModel):
    kind: Literal[ExprKind.DICT] = ExprKind.DICT
    items: list[DictItemDto] = Field(default_factory=list)
