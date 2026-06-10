from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.value_object import ValueObject


class BehaviorSyncData(ValueObject):
    name: str
    description: str
    inputs: list[AttributeSyncData]
    output: TypeDef
    body: list[AstStmt]
