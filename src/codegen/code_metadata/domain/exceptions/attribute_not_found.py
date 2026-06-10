from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.shared.domain.core.domain_exception import DomainException


class AttributeNotFound(DomainException):

    def __init__(
        self, attribute_id: AttributeId | None = None, attribute_name: str | None = None
    ) -> None:
        attr_info = "unknown"
        if attribute_id:
            attr_info = str(attribute_id)
        elif attribute_name:
            attr_info = attribute_name
        message = f"Attribute not found: Attribute `{attr_info}`"
        super().__init__(message)
