from __future__ import annotations
from typing import Any
from pydantic_core import core_schema
from foundation.building_blocks.value_object import ValueObject

class AstStmtBase(ValueObject):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        # 仅在校验或反序列化基类 AstStmtBase 本身时，将其重定向到联合类型 AstStmt
        # 若当前被解析的是具体的子类（如 AstIf、AstAssign），则正常通过 handler 生成其原本的 BaseModel schema
        if getattr(source_type, "__name__", None) == "AstStmtBase":
            def validate(v: Any) -> Any:
                # 使用 importlib 动态导入以避免 pyright 静态检查时的循环导入报错 (reportImportCycles)
                import importlib
                ast_stmt_module = importlib.import_module("codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt")
                return ast_stmt_module.ast_stmt_adapter.validate_python(v)
                
            def serialize(v: Any) -> Any:
                import importlib
                ast_stmt_module = importlib.import_module("codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt")
                return ast_stmt_module.ast_stmt_adapter.dump_python(v, mode="json")


            return core_schema.no_info_before_validator_function(
                validate,
                core_schema.any_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize,
                    when_used='always'
                )
            )
        
        return handler(source_type)

