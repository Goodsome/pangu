from typing import Literal
from typing import Any
from pydantic import field_serializer
from pydantic import field_validator
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject

_ELLIPSIS_MARKER = "__ellipsis__"
