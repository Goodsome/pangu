from codegen.code_metadata.domain.value_objects.scenario import Scenario
from codegen.code_metadata.application.dtos.type_def_dto import TypeDefDto
from pydantic import BaseModel
from codegen.code_metadata.application.dtos.attribute_dto import AttributeDto


class BehaviorDto(BaseModel):
    name: str
    description: str
    scenarios: list[Scenario]
    inputs: list[AttributeDto]
    output: TypeDefDto
