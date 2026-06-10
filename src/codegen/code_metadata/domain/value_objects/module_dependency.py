from collections.abc import Iterator
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.value_object import ValueObject


class ModuleDependency(ValueObject):
    module: ReferenceTarget
    component: ReferenceTarget | None
    type_checking: bool = False

    def iter_reference_targets(self) -> Iterator[ReferenceTarget]:
        yield self.module
        if self.component:
            yield self.component
