from typing import Annotated
from pydantic import Field
from pydantic.type_adapter import TypeAdapter
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.ast_await import AstAwait
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_bin_op import AstBinOp
from codegen.code_metadata.domain.value_objects.ast_bool_op import AstBoolOp
from codegen.code_metadata.domain.value_objects.ast_call import AstCall
from codegen.code_metadata.domain.value_objects.ast_compare import AstCompare
from codegen.code_metadata.domain.value_objects.ast_comprehension import (
    AstComprehension,
)
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_dict import AstDict
from codegen.code_metadata.domain.value_objects.ast_dict_comp import AstDictComp
from codegen.code_metadata.domain.value_objects.ast_formatted_value import (
    AstFormattedValue,
)
from codegen.code_metadata.domain.value_objects.ast_generator_exp import AstGeneratorExp
from codegen.code_metadata.domain.value_objects.ast_if_exp import AstIfExp
from codegen.code_metadata.domain.value_objects.ast_joined_str import AstJoinedStr
from codegen.code_metadata.domain.value_objects.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_lambda import AstLambda
from codegen.code_metadata.domain.value_objects.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_list_comp import AstListComp
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_set import AstSet
from codegen.code_metadata.domain.value_objects.ast_set_comp import AstSetComp
from codegen.code_metadata.domain.value_objects.ast_slice import AstSlice
from codegen.code_metadata.domain.value_objects.ast_starred import AstStarred
from codegen.code_metadata.domain.value_objects.ast_subscript import AstSubscript
from codegen.code_metadata.domain.value_objects.ast_tuple import AstTuple
from codegen.code_metadata.domain.value_objects.ast_unary_op import AstUnaryOp
from codegen.code_metadata.domain.value_objects.ast_yield import AstYield
from codegen.code_metadata.domain.value_objects.ast_yield_from import AstYieldFrom

AstExpr = Annotated[
    AstConstant
    | AstName
    | AstAttribute
    | AstCall
    | AstBinOp
    | AstBoolOp
    | AstUnaryOp
    | AstCompare
    | AstIfExp
    | AstLambda
    | AstJoinedStr
    | AstFormattedValue
    | AstListComp
    | AstSetComp
    | AstDictComp
    | AstGeneratorExp
    | AstSlice
    | AstStarred
    | AstSubscript
    | AstTuple
    | AstList
    | AstSet
    | AstDict
    | AstYield
    | AstYieldFrom
    | AstAwait,
    Field(discriminator="kind"),
]
ast_expr_adapter: TypeAdapter[AstExpr] = TypeAdapter(AstExpr)
Arg.model_rebuild()
AstAttribute.model_rebuild()
AstCall.model_rebuild()
AstBinOp.model_rebuild()
AstBoolOp.model_rebuild()
AstCompare.model_rebuild()
AstIfExp.model_rebuild()
AstLambda.model_rebuild()
AstJoinedStr.model_rebuild()
AstFormattedValue.model_rebuild()
AstListComp.model_rebuild()
AstSetComp.model_rebuild()
AstDictComp.model_rebuild()
AstGeneratorExp.model_rebuild()
AstSlice.model_rebuild()
AstStarred.model_rebuild()
AstSubscript.model_rebuild()
AstTuple.model_rebuild()
AstList.model_rebuild()
AstSet.model_rebuild()
AstDict.model_rebuild()
AstUnaryOp.model_rebuild()
AstYield.model_rebuild()
AstYieldFrom.model_rebuild()
AstAwait.model_rebuild()
AstKeyword.model_rebuild()
AstComprehension.model_rebuild()
