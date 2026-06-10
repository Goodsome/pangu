from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.domain_exception import DomainException


class DepComponentNotFound(DomainException):

    def __init__(self, component_id: ComponentId):
        self.component_id: ComponentId = component_id
        message = f"Dependency component not found for ID: {component_id}"
        super().__init__(message)
