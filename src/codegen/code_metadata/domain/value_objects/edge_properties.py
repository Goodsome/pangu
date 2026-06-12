from typing import Literal
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.shared.domain.core.value_object import ValueObject


class ImportsEdgeProperties(ValueObject):
    kind: Literal[EdgeType.IMPORTS] = EdgeType.IMPORTS
    is_type_checking: bool
