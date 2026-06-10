from pydantic import BaseModel
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class ParsedAttribute(BaseModel):
    name: str
    description: str
    type: ParsedType | None
    value: ParsedExpr | None = None
    value_v2: AstExpr | None = None
