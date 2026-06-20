from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.value_object import ValueObject


class DependsOnEdge(ValueObject):
    source: ModuleId
    target: ModuleId