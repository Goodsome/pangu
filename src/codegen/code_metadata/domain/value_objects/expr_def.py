from typing import Annotated
from pydantic import Field
from pydantic.type_adapter import TypeAdapter
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.lambda_expr import LambdaExpr
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr

ExprDef = Annotated[
    CallExpr | ConstantExpr | DictExpr | ReferenceExpr | SequenceExpr | LambdaExpr,
    Field(discriminator="kind"),
]
expr_def_adapter: TypeAdapter[ExprDef] = TypeAdapter(ExprDef)
