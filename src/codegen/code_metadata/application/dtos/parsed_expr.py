from typing import Annotated
from pydantic import Field
from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.lambda_expr_dto import LambdaExprDto
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto

ParsedExpr = Annotated[
    DictExprDto
    | ReferenceExprDto
    | ConstantExpr
    | CallExprDto
    | SequenceExprDto
    | LambdaExprDto,
    Field(discriminator="kind"),
]
