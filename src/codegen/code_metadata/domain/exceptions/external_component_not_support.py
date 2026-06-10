from codegen.shared.domain.core.domain_exception import DomainException


class ExternalComponentNotSupport(DomainException):

    def __init__(self, message: str):
        super().__init__(f"External component not support: {message}")
