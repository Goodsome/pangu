from codegen.shared.domain.core.value_object import ValueObject


class ReferenceSource(ValueObject):
    context: str
    components: list[str]
