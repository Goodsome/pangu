from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.core.value_object import ValueObject


class AttributeSyncData(ValueObject):
    name: str
    type: TypeDef | None
    value: ExprDef | None
