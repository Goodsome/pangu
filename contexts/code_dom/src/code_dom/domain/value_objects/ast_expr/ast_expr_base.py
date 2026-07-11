from __future__ import annotations
from typing import Any
from pydantic_core import core_schema
from foundation.building_blocks.value_object import ValueObject

class AstExprBase(ValueObject):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        # 仅在校验或反序列化基类 AstExprBase 本身时，将其重定向到联合类型 AstExpr
        if getattr(source_type, "__name__", None) == "AstExprBase":
            def validate(v: Any) -> Any:
                import importlib
                ast_expr_module = importlib.import_module("code_dom.domain.value_objects.ast_expr.ast_expr")
                return ast_expr_module.ast_expr_adapter.validate_python(v)
                
            def serialize(v: Any) -> Any:
                import importlib
                ast_expr_module = importlib.import_module("code_dom.domain.value_objects.ast_expr.ast_expr")
                return ast_expr_module.ast_expr_adapter.dump_python(v, mode="json")

            return core_schema.no_info_before_validator_function(
                validate,
                core_schema.any_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize,
                    when_used='always'
                )
            )
        
        return handler(source_type)
