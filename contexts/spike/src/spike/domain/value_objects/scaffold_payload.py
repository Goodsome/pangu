from typing import Annotated, Literal

from foundation.building_blocks.value_object import ValueObject
from pydantic import Field, TypeAdapter


from spike.domain.enums.method_type import MethodType
from spike.domain.enums.scaffold_type import ScaffoldType


class MethodPayload(ValueObject):
    method_type: MethodType = Field(description="The type of the method")
    method_name: str = Field(description="The name of the method")
    method_docstring: str = Field(description="The docstring of the method")
    method_args: list[str] = Field(
        description="The arguments of the method, separated by commas, e.g. 'arg1: str, arg2: int'"
    )
    method_return_type: str = Field(
        description="The return type of the method, must exist in the codebase"
    )


class BasePayload(ValueObject):
    prompt: str = Field(description="The prompt for creating the scaffold")
    context: str = Field(
        description="The context in which to create the dependency scaffold"
    )


class CommandScaffoldPayload(BasePayload):
    type: Literal[ScaffoldType.COMMAND] = ScaffoldType.COMMAND


class MethodScaffoldPayload(BasePayload, MethodPayload):
    type: Literal[ScaffoldType.METHOD] = ScaffoldType.METHOD


class DomainServiceScaffoldPayload(BasePayload):
    type: Literal[ScaffoldType.DOMAIN_SERVICE] = ScaffoldType.DOMAIN_SERVICE

    service_name: str = Field(description="The name of the domain service")
    method: MethodPayload = Field(description="The method of the domain service")


ScaffoldPayload = Annotated[
    CommandScaffoldPayload | MethodScaffoldPayload | DomainServiceScaffoldPayload,
    Field(discriminator="type"),
]


scaffold_payload_adapter: TypeAdapter[ScaffoldPayload] = TypeAdapter(ScaffoldPayload)
